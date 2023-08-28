#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
import numpy as np
import pandas as pd
import random
import pickle as pkl
import os
import time
import glob
import sys
import multiprocessing as mp
from tqdm import tqdm
import scipy
sys.path.append('../')
from compression.dictionary_encoding import *

from pattern_extraction.clustering_sampling import *
from utils.util_code import *

MAX_LENGTH = 50

def property_mining(log_seqs=None, 
                    log_meta=None,
                    eids=None,
                    var_lists=None,
                    param_lists=None,
                    num_col=None,
                    str_col=None,
                    threshold=0.1, 
                    sample_rate=0.01, 
                    n_candidates=128,
                    h=50, 
                    sampling=False,
                    random_sam=False,
                    parsing=True,
                    EE = True,
                    EH = True,
                    VV = True,
                    EV = True,
                    HH = True,
                    HV = True,
                    mt=0.5
                    ):
    # sampling = False
    print("step 4: relation mining")
    t1 = time.time()
    if sampling:
        print("step 4.1: sequence sampling")
        if random_sam:
            sampled_seqs_index  = {k: random.sample(range(len(log_seqs)), 1) for k in range(n_candidates)}
            print("random sampling")
        else:
            print("sequence based sampling")
            sampled_seqs_index = clustering_sampling(log_seqs, 
                                                 threshold=threshold, 
                                                sample_rate=sample_rate, 
                                                template_num=log_meta.template_num, 
                                                n_candidates=n_candidates)

        
        print("step 4.2: relation miner... ")
        t1 = time.time()
        mined_property = {}
        sampled_property = {"EH": [], "EE": [], "VV": []}
        tot_index = np.array([])
        for sid, idxs in sampled_seqs_index.items():
            ori_index = np.array([range(idx*h, min((idx+1)* h, len(log_meta.eids))) for idx in idxs])
            ori_index = np.hstack(ori_index)
            tot_index = np.concatenate([tot_index, ori_index])
        tot_index = tot_index.astype(int)

        sampled_eid = log_meta.eids[tot_index]
        sampled_var = log_meta.var_list[tot_index]
        
        param_lists = {}
        for i in range(log_meta.template_num):
            id_idx = np.where(sampled_eid==i)[0]
            param = np.array(sampled_var[id_idx].tolist()).T
            param_lists[i] = param
            
        headers = log_meta.headers[:,tot_index]
        # import pdb; pdb.set_trace()
        h_pat, header_arr, num_col, str_col = H_pat_miner(headers, mt=mt)
        v_pat, param_arr, v_num_col, v_str_col = V_pat_miner(param_lists, mt=mt)

        header_diff_r = {}
        param_diff_r = {}
        header_dict_r = {}
        param_dict_r = {}
        
        # diff_miner
        header_diff_r = num_col[diff_re_miner(header_arr[num_col])]
        header_dict_r = str_col[dict_re_miner(header_arr[str_col], mt=mt)]
        
        for eid in param_lists.keys():
            if param_arr[eid].shape[0] == 0:
                param_diff_r[eid] = np.array([])
                param_dict_r[eid] = np.array([])
            else:
                v_ncol = diff_re_miner(param_arr[eid][v_num_col[eid]])
                param_diff_r[eid] = v_num_col[eid][v_ncol]
                v_scol = dict_re_miner(param_arr[eid][v_str_col[eid]], mt=mt)
                param_dict_r[eid] = v_str_col[eid][v_scol]
            
        header_diff_r, param_diff_r, h_pat, v_pat = relation_matcher(log_meta, header_diff_r, param_diff_r, header_dict_r, param_dict_r, h_pat, v_pat)
    else:   
        h_pat, header_arr, num_col, str_col = H_pat_miner(log_meta.headers, parsing=parsing, mt=mt)
        v_pat, param_arr, v_num_col, v_str_col = V_pat_miner(log_meta.param_list, parsing=parsing, mt=mt)

        header_diff_r = {}
        param_diff_r = {}
        header_dict_r = {}
        param_dict_r = {}
        
        # diff_miner
        header_diff_r = num_col[diff_re_miner(header_arr[num_col])]
        header_dict_r = str_col[dict_re_miner(header_arr[str_col], mt=mt)]
        
        for eid in log_meta.param_list.keys():
            if param_arr[eid].shape[0] == 0:
                param_diff_r[eid] = np.array([])
                param_dict_r[eid] = np.array([])
            else:
                v_ncol = diff_re_miner(param_arr[eid][v_num_col[eid]])
                param_diff_r[eid] = v_num_col[eid][v_ncol]
                v_scol = dict_re_miner(param_arr[eid][v_str_col[eid]], mt=mt)
                param_dict_r[eid] = v_str_col[eid][v_scol]
            
        header_diff_r, param_diff_r, h_pat, v_pat = relation_matcher(log_meta, header_diff_r, param_diff_r, header_dict_r, param_dict_r, h_pat, v_pat)


    return {
        'hdiff': header_diff_r, 
        'pdiff': param_diff_r, 
        'hdict': header_dict_r, 
        'pdict': param_dict_r, 
        'h_pat': h_pat, 
        'v_pat': v_pat
        }


def relation_matcher(log_meta, header_diff_r, param_diff_r, header_dict_r, param_dict_r, h_pat, v_pat):
    # header
    # import pdb; pdb.set_trace()
    h_pat, log_meta.headers, header_diff_r, log_meta.header_num = pattern_matcher(log_meta.headers, h_pat, header_diff_r, header_dict_r, log_meta.header_dict)

    # param
    for i, arr in log_meta.param_list.items():
        v_pat[i], log_meta.param_list[i], param_diff_r[i], log_meta.num_col[i] = pattern_matcher(arr, v_pat[i], param_diff_r[i], param_dict_r[i], log_meta.var_dict)
    return header_diff_r, param_diff_r, h_pat, v_pat


def pattern_matcher(col_var, pat, diff_r, dict_r, dictionary):
    params = []
    new_pat = {}
    diff_i = []
    for j, carr in enumerate(col_var):
        if j in pat:
            # What if not match ??
            suc, new_arr = pattern_matcher_unit(pat[j], carr)
            if suc:
                params.append(new_arr)
                new_pat[j] = pat[j]
            else:
                params.append(carr.reshape(1,-1))
        else:
            params.append(carr.reshape(1,-1))
    if len(params):
        params = np.concatenate(params)
    else:
        params = np.array([])
    new_params = []
    res = np.array([isnumeric(x) for x in params])
    num_col = np.where(res==True)[0]
    for i, arr in enumerate(params):
        if i in diff_r:
            try:
                new_params.append([diff_matcher(arr.astype(int))])
                diff_i.append(i)
            except:
                new_params.append([arr])
        elif i in dict_r:
            new_params.append([dict_matcher(dictionary, arr)])
        else:
            new_params.append([arr])
        
    if len(new_params):
        new_params = np.concatenate(new_params)
        # print(new_params)
    else:
        new_params = np.array([])
    return new_pat, new_params, diff_i, num_col


def diff_matcher(col_var):
    diff_value = np.diff(col_var)
    diff_value = np.insert(diff_value, 0, col_var[0])
    return diff_value

def dict_matcher(dictionary, col_var):
    def mapping_func(cur_dict, x):
        if x in cur_dict:
            return cur_dict[x]
        else:
            cur_dict[x] = len(cur_dict)
            return len(cur_dict) - 1
    func = np.vectorize(mapping_func)
    dict_value = func(dictionary, col_var)
    dict_value = diff_matcher(dict_value)
    return dict_value


def H_pat_miner(header_str=None, parsing=True, mt=0.5):
    
    print("H H mining")
    h_pat = {}
    num_col = []
    str_col = []
    # import pdb; pdb.set_trace()
    h_pat, arr,  num_col, str_col = variable_fine_grained_parser(header_str, parsing=parsing, mt=mt)
    
    return h_pat, arr, num_col, str_col


def V_pat_miner(param_list, parsing=True, mt=0.5):
    print("E V mining")
    var = {}
    v_pat = {}
    num_col = {}
    str_col = {}
    # new_param
    for eid in param_list:
        v_pat[eid], var[eid], num_col[eid], str_col[eid] = variable_fine_grained_parser(param_list[eid], parsing=parsing, mt=mt)
                    
    return v_pat, var, num_col, str_col

def entropy_cal(seq):
    count_dict = Counter(seq)
    count = list(count_dict.values())
    weights = []
    for i in count_dict.keys():
        weights.append(np.log2(np.abs(i) + 1))
    weights = np.array(weights)
    pp = np.array(count) / len(seq)
    ent = -np.sum(pp * np.log(pp) * weights)
    return ent
      
      
def diff_re_miner(col_var):      
    diff_r = []
    for i in range(len(col_var)):
        if diff_re_unit(col_var[i].astype(int)):
            diff_r.append(i)
    return diff_r

def dict_re_miner(col_var, mt=0.5):
    dict_r = []
    for i in range(len(col_var)):
        if dict_re_unit(col_var[i], mt):
            dict_r.append(i) 
    return dict_r

def diff_re_unit(seq):
    diff_value = np.diff(seq)
    before_entropy = entropy_cal(seq)
    after_entropy = entropy_cal(diff_value)
    return before_entropy >= after_entropy

def dict_re_unit(seq, threshold=0.5):
    return len(set(seq)) < threshold * len(seq)
    
def variable_fine_grained_parser(col_var, parsing=True,mt=0.3):
    v_pat = {}
    arr_list = []
    if len(col_var) == 0:
        return [], col_var, np.array([]),  np.array([])
    # now_col = len(col_var)
    for i, var in enumerate(col_var):
        
        if len(set(var)) > mt * len(var):
            pat = pattern_miner(var)
            # TODO: test!!!!
            if parsing is False:
                pat = ''
            if pat != '':
                suc, arr = pattern_matcher_unit(pat, var)
                if suc:
                    arr_list.append(arr)
                    v_pat[i] = pat
                else:
                    arr_list.append(var.reshape(1,-1))
            else:
                arr_list.append(var.reshape(1,-1))
        else:
            arr_list.append(var.reshape(1,-1))
    try: 
        arr = np.concatenate(arr_list, axis=0)
    except:
        import pdb; pdb.set_trace()
    res = np.array([isnumeric(x) for x in arr])
    num_col = np.where(res==True)[0]
    str_col = np.where(res==False)[0]
    return v_pat, arr, num_col, str_col

    
def lcs_recursive(seq1, seq2, idx1 = 0, idx2 = 0):
    
    if idx1 == len(seq1) or idx2 == len(seq2):
        return ""
        
    if seq1[idx1] == seq2[idx2]:
        return  seq1[idx1] + lcs_recursive(seq1, seq2, idx1 + 1, idx2 + 1)
    
    else:
        option1 = lcs_recursive(seq1, seq2, idx1 + 1, idx2)
        option2 = lcs_recursive(seq1, seq2, idx1, idx2 + 1)
        
        
        return max(option1, option2, key = len)
           
def pattern_miner(var):
    delimiters = "-#><_:;,[]\\/.()"
    if len(var) == 0:
        return var
    
    def sfunc(x, sep):
        res = ""
        for i in x:
            if i in sep:
                res += i
        return res
    
    func = np.vectorize(sfunc)
    res = func(var, delimiters)
    pat = res[0]
    for i in range(1, len(res)):
        pat = lcs_recursive(pat, res[i])
        if len(pat) == 0:
            break

    return pat

def pattern_matcher_unit(pat, var):
    
    def split_arr_vec(var_i, pat_i):
        res = []
        lpos = 0
        for p in pat_i:
            pos = var_i[pos:].find(p)
            if pos == -1:
                return None

            if lpos != pos:
                res.append(var_i[lpos:pos])
            lpos = pos + 1
        return res
        
    def split_arr(var_i, pat_i):
        res = []
        length = -1
        for i in var_i:
            cur = []
            lpos = 0
            for p in pat_i:
                pos = i[lpos:].find(p)
                if pos == -1:
                    return None
                if lpos != pos:
                    cur.append(i[lpos:pos+lpos])
                    lpos = lpos + pos + 1
            if lpos < len(i):
                cur.append(i[lpos:])
            if length != -1 and len(cur) != length:
                return None
            if length == -1:
                length = len(cur)
            res.append(cur)
            
        return np.array(res)
        
    arr = split_arr(var, pat)
    
    # func = np.vectorize(split_arr_vec)
    # splited_arr = func(var, pat)
    # if np.isnan(splited_arr).any():
    #     return False, None
    # else:
    #     return True, splited_arr
    
    if arr is not None:
        arr = arr.T
        return True, arr
    else:
        return False, None
    # for i in range(arr.shape[0]):
    #     # print(arr[i])
    #     if np.char.isnumeric(arr[i]).all():
    #         diff_value = np.diff(arr[i].astype(int))
    #         # print(diff_value)
    #         arr[i] = np.insert(diff_value, 0, arr[i][0])
    # # arr = np.hstack(arr)
    return arr
    
    