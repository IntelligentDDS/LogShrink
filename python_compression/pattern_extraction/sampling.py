# Copyright refers to: https://github.com/LogIntelligence/LogPPT/blob/master/logppt/sampling/__init__.py
import textdistance
import random
from Levenshtein import distance
from tqdm import tqdm
import numpy as np
from scipy.spatial.distance import cdist, pdist
import sys
sys.path.append("../")
from utils.Logger import *

def euc_distance(x, y):
    return textdistance.cosine.normalized_distance(x[0], y[0])

def random_sampling(input_data=None, sample_rate=0.1):
    """ do randomly sampling from a large input_data with given sample_rate.

    Args:
    --------
    input_data: input large data matrix to be sampled.
    sample_rate: float number, e.g., 0.1 represents 10 is selected out of 100 data instances.

    Returns:
    --------
    sample_data: the sampled data
    """
    m = int(len(input_data) * sample_rate)
    # m = 60
    if m > 100:
        m = 100
    elif m <= 0:
        m = 1

    sample_ids = sorted(random.sample(range(len(input_data)), m))
    sample_data = []
    start = 0
    for i, line in enumerate(input_data):
        if start < len(sample_ids) and i == sample_ids[start]:
            start += 1
            sample_data.append(line)

    sample_data = np.array(sample_data)
    log("debug",
        'Step 1. Sampling with sample_rate %.3f, the original data size is %d, after sampling, the data size is %d'
        % (sample_rate, input_data.shape[0], sample_data.shape[0]))
    return sample_ids, sample_data

def random_sampling_seq(input_data=None, n_candidate=64):
    """ do randomly sampling from a large input_data with given sample_rate.

    Args:
    --------
    input_data: input large data matrix to be sampled.
    sample_rate: float number, e.g., 0.1 represents 10 is selected out of 100 data instances.

    Returns:
    --------
    sample_data: the sampled data
    """

    sample_ids = sorted(random.sample(range(len(input_data)), n_candidate))
    sample_data = []
    start = 0
    for i, line in enumerate(input_data):
        if start < len(sample_ids) and i == sample_ids[start]:
            start += 1
            sample_data.append(line)

    sample_data = np.array(sample_data)
    return  sample_data

def lev_distance(x, y):
    return distance(x, y)

def min_distance_1(c_set, t_set, func, s_threshold=0.05, u_threshold=0.7):
    D = []
    c_set = np.array(c_set).reshape(-1,1)
    t_set = np.array(t_set).reshape(-1,1)
    distance_matrix = cdist(c_set, t_set, func)
    min_list = np.min(distance_matrix, axis = 1)
    
    return min_list


def adaptive_random_sampling(seqs, k, cluster_min_len=3, n_candidate=128):
    sample_set = []
    pattern_num = 0
    r = 0
    n = 0
    for i in range(k):
        # print(r)
        if len(sample_set) == 0:
            i = random.randint(0, n_candidate)
            sample_set.append(seqs[i])
            continue
        sample_set_ids = random.sample(range(len(seqs)), n_candidate)
        candidate_set = [
            seqs[x] for x in range(len(seqs)) if x in sample_set_ids
        ]
        min_list = min_distance_1(candidate_set, sample_set, euc_distance, s_threshold=0.2, u_threshold=0.6)
        best_candidate = max(range(len(min_list)), key=min_list.__getitem__)
        sample_set.append(candidate_set[best_candidate])

    return sample_set




def min_distance(c_set, t_set, func, s_threshold, u_threshold):
    D = []
    c_set = np.array(c_set).reshape(-1,1)
    t_set = np.array(t_set).reshape(-1,1)
    distance_matrix = cdist(c_set, t_set, func)
    min_list = np.min(distance_matrix, axis = 1)
    min_index_list = np.argmin(distance_matrix, axis = 1)
    
    # select same sequence patterns
    validMinList = distance_matrix[np.arange(len(min_index_list)), min_index_list] < s_threshold
    same_results = np.array([min_index_list[i] if x else -1 for i, x in enumerate(validMinList)])
    validMaxList = distance_matrix[np.arange(len(min_index_list)), min_index_list] > u_threshold
    diff_results = np.array([min_index_list[i] if x else -1 for i, x in enumerate(validMaxList)])
    max_idx = max(range(len(min_list)), key=min_list.__getitem__)
    # import pdb; pdb.set_trace()
    # max_one
    return same_results, diff_results, max_idx


# 1. candidate distance if min is smaller than a threshold, consider them as the same sequence pattern
# 2. add several candidates every time
def adaptive_sequence_sampling(seqs, k, cluster_min_len=3, n_candidate=128):
    sample_set = {}
    pattern_num = 0
    r = 0
    centers = []
    n = 0
    while r < k:
        # print(r)
        if len(sample_set) == 0:
            i = random.randint(0, n_candidate)
            sample_set[pattern_num] = [seqs[i]]
            centers.append(seqs[i])
            pattern_num += 1
            r += 1
            continue
        sample_set_ids = random.sample(range(len(seqs)), n_candidate)
        candidate_set = [
            seqs[x] for x in range(len(seqs)) if x in sample_set_ids
        ]
        same_results, diff_reuslts, max_idx = min_distance(candidate_set, centers, euc_distance, s_threshold=0.2, u_threshold=0.6)
        
        # select the minimum list as the same pattern              
        for i in range(len(same_results)):
            if same_results[i] >= 0 and same_results[i] < pattern_num:
                clu_result = same_results[i]
                if len(sample_set[clu_result]) < cluster_min_len:
                    sample_set[clu_result].append(candidate_set[i])
                    n += 1
                    # print(n)
                    r += 1

        flag = True
        # select the maximum list as the different pattern
        for i in range(len(diff_reuslts)):
            if diff_reuslts[i] >= 0:
                sample_set[pattern_num] = [candidate_set[i]]
                centers.append(candidate_set[i])
                pattern_num += 1
                r += 1
                flag = False

        if flag:
            sample_set[pattern_num] = [candidate_set[max_idx]]
            centers.append(candidate_set[max_idx])
            pattern_num += 1
            r += 1

    return sample_set

