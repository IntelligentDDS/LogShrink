#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import random
import time
import os
from utils.Logger import *
from LogMeta import LogMeta



def preprocess_encoding(log_meta, outdir: str, dict_column_mode: bool, prefix_mode:bool, re_mode:bool):
    t1 = time.time()
    dictionary_replacing_header(log_meta,
                        outdir=outdir,
                        outfile="header_dict",
                        dict_column_mode=dict_column_mode,
                        prefix_mode=prefix_mode)

    dictionary_replacing_var(log_meta,
                            outdir=outdir,
                            outfile="var_dict",
                            dict_column_mode=dict_column_mode,
                            prefix_mode=prefix_mode)
    
    
    # log_meta.header_str = get_diff_df(log_meta.header_str)
    log("info", "encoding takes %.3f s", time.time() - t1)
    # return headers_str, var_lists


def get_diff_df(df: pd.DataFrame()):
    df = df.astype(int)
    diff = df.diff()
    diff.iloc[0, :] = df.iloc[0, :]
    diff = diff.astype(int)
    del df
    return diff

def dictionary_replacing_header(log_meta, outdir="", outfile="", dict_column_mode=True, prefix_mode=True):
    dictionary = dict()
    def mapping_func(cur_dict, x):
        if x in cur_dict:
            return cur_dict[x]
        else:
            cur_dict[x] = len(cur_dict)
            return len(cur_dict) - 1
        
    common_prefix = []
    common_suffix = []
    for c in range(len(log_meta.header_str)):
        if dict_column_mode:
            dictionary[c] = {}
            _dict = dictionary[c]
        else:
            _dict = dictionary
            
        if prefix_mode:
            prefix, suffix, log_meta.header_str[c] = extract_common_prefix_suffix(log_meta.header_str[c])
            common_prefix.append(prefix)
            common_suffix.append(suffix)
        
        func = np.vectorize(mapping_func)
        log_meta.header_str[c]= func(_dict, log_meta.header_str[c])
        
    # output dictionary
    if dict_column_mode:
        for c in range(len(log_meta.header_str)):
            output_dict(dictionary[c], outdir=outdir, outfile=outfile + str(c))
    else:
        output_dict(dictionary, outdir=outdir, outfile=outfile)



def dictionary_replacing_var(log_meta, outdir="", dict_column_mode=True, prefix_mode=True, skip_index=None, outfile=""):
    dictionary = dict()
    # TODO: store common prefix
    common_prefix = []
    common_suffix = []
    def foo_func(x, cur_dict):
        if x not in cur_dict:
            cur_dict[x] = len(cur_dict)
        return cur_dict[x]
    
    
    new_param_list = {}
    for eid, val in log_meta.param_list.items():
        new_param_list[eid] = []
        if dict_column_mode:
            dictionary[eid] = {}
            _dict = dictionary[eid]
        else:
            _dict = dictionary
        # para_list = np.array(val.tolist()).T
        for i in range(len(val)):
            if i in log_meta.num_col[eid]: 
                if type([i]) == list:
                    new_param_list[eid].append(np.array(val[i]).astype(int))
                else:
                    new_param_list[eid].append(val[i].astype(int))
                continue
            if len(val[i]) == 0: continue
            if dict_column_mode:
                if i not in _dict:
                    _dict[i] = {}
                __dict = _dict[i]
            else:
                __dict = dictionary
            if prefix_mode:                    
                prefix, suffix, val[i] = extract_common_prefix_suffix_list(val[i].tolist())
                common_prefix.append(prefix)
                common_suffix.append(suffix)

            func = np.vectorize(foo_func)
            val[i] = func(val[i], __dict)
            
            new_param_list[eid].append(val[i].astype(int))
    
    log_meta.param_list = new_param_list
    if dict_column_mode:
        for eid, val in dictionary.items():
            for col, cval in val.items():
                output_dict(cval, outdir=outdir, outfile=outfile + str(eid) + '_' + str(col))
    else:
        output_dict(dictionary, outdir=outdir, outfile=outfile)
        
    
def extract_common_prefix_suffix_list(series):
    prefix, param = extract_common_prefix_list(series)
    reversed_list = [s[::-1] for s in param]
    suffix, param = extract_common_prefix_list(reversed_list)
    param = [s[::-1] for s in param]
    return prefix, suffix, param
    
def output_dict(d, outdir="", outfile=""):
    with open(os.path.join(outdir, outfile + ".dict"), "w") as f:
        for key in sorted(d.keys(), key=d.get):
            f.write("{}\n".format(key))
            
            
def extract_common_prefix_suffix(series):
    prefix, param = extract_common_prefix(series)
    reversed_list = [s[::-1] for s in param]
    suffix, param = extract_common_prefix_list(reversed_list)
    param = [s[::-1] for s in param]
    return prefix, suffix, pd.Series(param)

def extract_common_prefix(series):
    common_prefix = os.path.commonprefix(series.values.tolist())
    series = series.str.removeprefix(common_prefix)
    return common_prefix, series

def extract_common_prefix_list(l_list):
    common_prefix = os.path.commonprefix(l_list)
    series = list(map(lambda x: x.replace(common_prefix, ''), l_list))
    return common_prefix, series   