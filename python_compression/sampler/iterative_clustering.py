#!/usr/bin/env python
# -*- coding: utf-8 -*-
from utils.Logger import *
from tqdm import tqdm
from python_compression.sampler.similarity_function import *
from python_compression.sampler.sampling import random_sampling
import numpy as np
import pandas as pd
import random
import pickle as pkl
import os
import time
import glob
import sys
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn import linear_model
import multiprocessing
from scipy.spatial.distance import cdist, pdist
import math
from collections import Counter

sys.path.append("../")


# def iterative_clustering(input_data=None,
#                          sample_rate=0.1,
#                          threshold=0.6,
#                          templates_number=0,
#                          template_min_len=20,
#                          terminated_num=200,
#                          cluster_min_len=3):
#     """ the whole workflow

#     Args:
#     --------
#     input_data: input large data matrix to be sampled.
#     sample_rate: sample percentage, integer number, e.g., 100 represents one is selected out of 100 data instances.

#     Returns:
#     --------
#     sample_data: the sampled data
#     """
#     print("WHATTTTTT")
#     log("debug", "Step 2, iterative clustering")
#     # ordered
#     input_data = np.array(input_data)
#     mismatch_data = input_data

#     mismatch_raw_index = np.arange(len(input_data))
#     onehot_encoding_all = onehot_encoding(input_data, templates_number)
#     # clu_result = []
#     # cids = {i: -1 for i in range(len(input_data))}
#     cids = {}
#     seq_diffs = {}
#     hit_maps = {}
#     templates_pool = []
#     i = 0
#     st = time.time()
#     zero_count = 0
#     while zero_count <= terminated_num and len(mismatch_raw_index) > 100:
#         log("debug", "=========================Round %d =========================" %
#               i)
#         if i == 0:
#             t =  0
#             template_min_len_cur = input_data.shape[1]
#         else:
#             t =  threshold
#             template_min_len_cur = template_min_len
#         i += 1
#         sampled_ids, sampled_data = random_sampling(mismatch_raw_index, sample_rate)
#         # ordered
#         clusters = clustering(input_data[sampled_data], onehot_encoding_all[sampled_data], t, templates_number)
#         templates = pattern_extraction(clusters, cluster_min_len,
#                                        template_min_len_cur)

#         if len(templates) == 0:
#             zero_count += 1
#             continue
#         zero_count = 0
#         # matching
#         mismatch_raw_index, cluster_result, parameter_list, hit_map = sequence_matching(
#             templates, mismatch_raw_index, mismatch_data, templates_number,
#             len(templates_pool), onehot_encoding_all[mismatch_raw_index])
#         # update mismatch data
#         mismatch_data = input_data[mismatch_raw_index]
#         cids.update(cluster_result)
#         seq_diffs.update(parameter_list)
#         templates_pool.extend(templates)
#         hit_maps.update(hit_map)

#     # check length
#     if (len(cids) + len(mismatch_data)) != input_data.shape[0]:
#         log("debug", "CLUSTERING RESULTS LENGTH UNMATCH")
#         exit(1)

#     cids_array = [-1] * input_data.shape[0]
#     for i, val in cids.items():
#         cids_array[i] = val

#     log("info",
#         "Iterative clustering took %.3f s, generating %d clusters and %d mismatched data"
#         % (time.time() - st, len(templates_pool), len(mismatch_data)))
#     print("Iterative clustering took %.3f s, generating %d clusters and %d mismatched data"
#             % (time.time() - st, len(templates_pool), len(mismatch_data)))
#     center_idxs = get_center_idxs(cids, len(templates_pool))
#     return center_idxs, templates_pool, cids_array, list(seq_diffs.values()), hit_maps

def iterative_clustering_seq(input_data=None,
                             sample_rate=0.1,
                             threshold=0.6,
                             templates_number=0,
                             terminated_num=200,
                             cluster_min_len=3):
    """ the whole workflow

    Args:
    --------
    input_data: input large data matrix to be sampled.
    sample_rate: sample percentage, integer number, e.g., 100 represents one is selected out of 100 data instances.

    Returns:
    --------
    sample_data: the sampled data
    """
    log("debug", "Step 2, iterative clustering")
    st = time.time()
    input_data = np.array(input_data)
    mismatch_raw_index = np.arange(len(input_data))
    onehot_encoding_all = onehot_encoding(input_data, templates_number)

    cids = {}
    i = 0
    zero_count = 0
    centers = []
    while zero_count <= terminated_num and len(mismatch_raw_index) > 1:
        log("debug", "=========================Round %d =========================" %
            i)
        i += 1
        sampled_ids, sampled_data = random_sampling(
            mismatch_raw_index, sample_rate)
        # ordered
        clusters = clustering(
            input_data[sampled_data], onehot_encoding_all[sampled_data], threshold, templates_number)
        repres = repres_extracting(clusters, cluster_min_len)

        if len(repres) == 0:
            zero_count += 1
            continue
        mismatch_raw_index, cluster_result = matching(
            repres, onehot_encoding_all[mismatch_raw_index], threshold, mismatch_raw_index)

        if len(cluster_result) == 0:
            zero_count += 1
            continue
        zero_count = 0

        # update clustering centers and matching index
        cluster_result = {k + len(centers): val for k,
                          val in cluster_result.items()}

        centers.extend(repres)
        cids.update(cluster_result)

    log("info",
        "Iterative clustering took %.3f s, generating %d clusters and %d mismatched data"
        % (time.time() - st, len(centers), len(mismatch_raw_index)))
    print("Iterative clustering took %.3f s, generating %d clusters and %d mismatched data"
          % (time.time() - st, len(centers), len(mismatch_raw_index)))
    return cids, centers


def get_center_idxs(cids=None, clusters_num=0):
    center_idxs = {}
    for key, val in cids.items():
        if val not in center_idxs:
            center_idxs[val] = key
        if len(center_idxs) == clusters_num:
            break
    return center_idxs


def clustering(data=None, fm=None, threshold=0.6, templates_number=0):
    """ cluster log sequence vectors into various clusters.

    Args:
    --------
    para: the dictionary of parameters, set in run.py
    data: the data matrix used for clustering

    Returns:
    --------
    seq_clusters: list of lists, data of each cluster is stored in one list, various clusters composes a large list
    """
    log("debug", 'Step 3. Distance Calculation: start building distance matrix')
    t_disMat = time.time()
    # fm = data
    # data_dist = distance_compute(data, ngram_2_distance)
    data_dist = distance_compute(fm, "euclidean")
    # import pdb; pdb.set_trace()
    log("debug", "------Distance Calculation finished, it takes %.15f seconds" %
        (time.time() - t_disMat))

    # check whether the number of distances is correct
    instNum = data.shape[0]
    if len(data_dist) != (instNum - 1) * instNum / 2:
        log("debug", 'Error distance matrix size, recomputing')
        data_dist = distance_compute(fm)

    # special case handling: if only one vector in the data, no need to do clustering, directly return the data.
    if instNum == 1:
        return [[fm[0]]]

    # HAC clustering
    clusterLabels = HAC_clustering(data_dist, threshold)
    # clusterLabels = hdbscan_clustering(data_dist, threshold)
    # use hierarchical clustering
    log("debug", 'Step 4. Clustering, start hierarchical clustering')

    clusNum = len(set(clusterLabels))
    log("debug",
        '------there are altogether ## %d ## clusters in current clustering' %
        (clusNum))

    # get cluster list
    # ！！！！TEMPP
    seq_clusters = [[] for _ in range(clusNum)]
    for i, ci in enumerate(clusterLabels):
        seq_clusters[ci - 1].append(fm[i])
    return seq_clusters


def repres_extracting(seq_clusters, cluster_min_len):
    """ extract the representative vector for each cluster of data.
    Args:
    --------
    seq_clusters: list of clusters of sequence data
    Returns:
    --------
    repre_seqs: list of representatives
    """
    # import pdb; pdb.set_trace()
    repre_seqs = []
    for clu in seq_clusters:
        if len(clu) < cluster_min_len:
            continue
        # print(clu)
        repre_seqs.append(np.mean(clu, axis=0))
        # repre_seqs.append(clu[0])
    repre_seqs = np.array(repre_seqs)
    return repre_seqs


def HAC_clustering(data_dist, threshold):
    Z = linkage(data_dist, 'complete')
    clusterLabels = fcluster(Z, threshold, criterion='distance')
    return clusterLabels


def pattern_extraction(clusters=None, cluster_min_len=3, template_min_len=20):
    log("debug", 'Step 5. Pattern Extraction')
    templates = []
    count = []
    # import pdb ; pdb.set_trace()
    for cluster in clusters:
        # drop those cluster with only one sample
        if len(cluster) < cluster_min_len:
            continue
        template = cluster[0]
        length = 0
        for seq in cluster:
            length, template = LCS(template, seq)
            template = merge_template(template)
        length = len(template) - template.count('<*>')
        if length < template_min_len:
            continue
        templates.append(template)
        count.append(length)
        # log("debug", template)

    new_templates = templates
    log("debug", "After Pattern Extraction, each cluster template length is ", count)
    log("debug", "After filtering, remaining %d clusters" % (len(new_templates)))
    # filtering those short templates
    return new_templates


def seq_match(seq, templates, count):
    # prune those unmatched first
    for i in range(len(templates[0])):
        if (seq[1] < templates[1][i]).any():
            continue
        template = templates[0][i]
        flag = True
        pos = 0
        parameter_list = []
        hit_map = []
        for subseq in template:
            var = []
            flag2 = False
            for j in range(pos, len(seq[0])):
                if (j + len(subseq)) > len(seq[0]):
                    flag = False
                    break
                # comparison between nd array
                if (seq[0][j:j + len(subseq)] == subseq).all():
                    pos = j + len(subseq)
                    flag2 = True
                    hit_map.extend([True]*len(subseq))
                    if len(var):
                        parameter_list.append(var)
                        hit_map.extend([False]*len(var))
                    break
                var.append(seq[0][j])
            flag = flag & flag2
            if not flag:
                break
        # add all the rest to parameter list
        parameter_list.append(seq[0][pos:].tolist())
        hit_map.extend([False]*(len(seq[0]) - pos))
        if flag:
            return i + count, parameter_list, hit_map
    return -1, None, None


def preprocess_templates(templates):
    # separate all the templates by <*>
    temp_list = list()
    for template in templates:
        temp = []
        cur = []
        for t in template:
            if t == '<*>':
                if len(temp):
                    cur.append(temp)
                    temp = []
            else:
                temp.append(t)
        if len(temp):
            cur.append(temp)
        temp_list.append(cur)
    return temp_list


def sequence_matching(templates, raw_index, input_data, templates_number,
                      count, fm):
    t1 = time.time()
    log("debug", "Step 6. sequence Matching, start matching with original data")
    # one hot encoding:
    # time complexity: O(n* h) 3600*50 = 1.9 * 10 ** 5
    template_fm = onehot_encoding(templates, templates_number)
    templates_merge = preprocess_templates(templates)
    # import pdb; pdb.set_trace()
    # do it in parallels
    cluster_array = list(
        map(lambda x: seq_match(x, (templates_merge, template_fm), count),
            zip(input_data, fm)))
    cids = np.array([res[0] for res in cluster_array])
    parameters = [res[1] for res in cluster_array]
    hit_map = [res[2] for res in cluster_array]

    if -1 in cids:
        mismatch_index = np.where(cids == -1)[0]  # mismatched sequence indexes
    else:
        mismatch_index = []
    # remapping

    cluster_result = {}
    parameter_list = {}
    hit_map_dict = {}
    match_index = np.where(cids != -1)[0]
    for i in range(len(match_index)):
        cluster_result[raw_index[match_index[i]]] = cids[match_index[i]]
        parameter_list[raw_index[match_index[i]]] = parameters[match_index[i]]
        hit_map_dict[raw_index[match_index[i]]] = hit_map[match_index[i]]

    mismatch_raw_index = raw_index[mismatch_index]
    t2 = time.time()
    log("debug", '------matching takes %.15f seconds, %d sequences are not matched' %
        (t2 - t1, len(mismatch_index)))

    return mismatch_raw_index, cluster_result, parameter_list, hit_map_dict


def matching(centers, input_data, threshold, raw_index):
    """ match all weighted data (1st round) or mismatched data (other rounds) with cluster representatives.

    Args:
    --------
    raw_data: unweighted raw data. it is used for saving into files, raw data are saved without weighting.

    Returns:
    --------
    mismatch_index: index for mismatched data
    """
    t1 = time.time()
    log("debug", "Step 6. Matching, start matching with original data")
    # padding to fixed-length
    distance_matrix = cdist(input_data, centers, "euclidean")
    min_index_list = np.argmin(distance_matrix, axis=1)
    validMinList = distance_matrix[np.arange(
        len(min_index_list)), min_index_list] < threshold
    clu_result = np.array(
        [min_index_list[i] if x else -1 for i, x in enumerate(validMinList)])

    # get the mismatched data with its index
    if -1 in clu_result:
        # mismatched sequence indexes
        mismatch_index = np.where(clu_result == -1)[0]
    else:
        mismatch_index = []

    # initialize cluster_result
    cluster_result = dict()
    for i in range(max(clu_result) + 1):
        match_index = np.where(clu_result == i)[0]
        # map to raw index
        cluster_result[i] = raw_index[match_index]

    # update mismatch raw index
    mismatch_raw_index = raw_index[mismatch_index]
    t2 = time.time()
    log("debug", '------matching takes %.15f seconds, %d sequences are not matched' %
        (t2 - t1, len(mismatch_index)))
    return mismatch_raw_index, cluster_result


def onehot_encoding(data, templates_number):
    # t1 = time.time()
    frequency = list(map(Counter, data))
    frequency.append({i: 0 for i in range(templates_number)})
    df = pd.DataFrame(frequency,
                      columns=[i for i in range(-1, templates_number)])

    df.fillna(value=0, inplace=True)
    data = df.values[:-1, 1:]
    weight = weighting(data, templates_number)

    weighted_embed = np.multiply(data, weight)
    return weighted_embed


def weighting(data, templates_number):
    weightList = []
    for j in range(templates_number):
        cnt = np.count_nonzero(data[:, j])
        weightList.append(math.log((data.shape[0] + 1) / (float(cnt) + 1)))
    weightList -= np.mean(weightList)
    newweightList = np.array([1 / float(1 + np.exp(- x)) for x in weightList])

    return newweightList


def distance_compute(data, similarity_func):
    """ calculate the distance between any two vectors in a matrix.

    Args:
    --------
    data: the data matrix whose distances will be calculated.

    Returns:
    --------
    dist_list: flatten distance list
    """
    dis = pdist(data, similarity_func)
    zeroarray = np.zeros(len(dis))
    dist_list = np.maximum(dis, zeroarray)  # to avoid negative distance
    return dist_list


def merge_template(template):
    # merge all the astrick
    start = -1
    new_template = []
    for i, token in enumerate(template):
        if token == '<*>':
            if start == -1:
                start = i
        else:
            if start == -1:
                new_template.append(token)
            else:
                new_template.append('<*>')
                new_template.append(token)
                start = -1
    if start != -1:
        new_template.append('<*>')
    return new_template
