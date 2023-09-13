

import argparse
import re
import os
import time
import sys
import json
import shutil
import tarfile
import numpy as np
from subprocess import call
import json
import ast


def unzip_tool(kernel="lzma", input_file="", output_dir=""):
    if kernel == "lzma":
        lzma_cmd = f"7za x {input_file} -o{output_dir}"
        call(lzma_cmd, shell=True)
    elif kernel == 'gzip':
        file = tarfile.open(input_file, 'r:gz')
        file.extractall(output_dir)
        file.close()
    elif kernel == 'bz2':
        file = tarfile.open(input_file, 'r:bz2')
        file.extractall(output_dir)
        file.close()


def load_relations(relation_file):
    # 3 files: diff, dict, pat
    # header: hdiff, hdict, h_pat
    pdiff = load_json(relation_file + '.pdiff')
    pdict = load_json(relation_file + '.pdict')
    p_pat = load_json(relation_file + '.v_pat')
    
    hdiff = load_int_array(relation_file + '.hdiff')
    hdict = load_int_array(relation_file + '.hdict')
    h_pat = load_json(relation_file + '.h_pat')
    
    return {'pdiff': pdiff, 'pdict': pdict, 'v_pat': p_pat, 'hdiff': hdiff, 'hdict': hdict, 'h_pat': h_pat}
    
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def load_dict(filename):
    dict_res = dict()
    with open(filename, 'r') as file:
        for i, line in enumerate(file.readlines()):
            dict_res[i] = line.strip()
    return dict_res
            
    
def load_int_array(filename):
    arr = []
    with open(filename, 'r') as file:
        for line in file:
            arr.append(int(line))
    return arr
    
def load_str_array(filename):
    arr = []
    with open(filename, 'r') as file:
        for line in file:
            arr.append(line.strip())
    return arr

def load_str_array_raw(filename):
    arr = []
    with open(filename, 'r') as file:
        for line in file:
            arr.append(line)
    return arr


def recover_dict(arr, dict):
    res = []
    for v in arr:
        res.append(dict[v])
    return res

def recover_diff(arr):
    res = np.zeros(len(arr), dtype=int)
    res[0] = arr[0]
    for i in range(1, len(arr)):
        res[i] = res[i-1] + arr[i]
    # res = 
    return res
    
# adapt from log reducer
def elastic_decoder(filename):
    new_path = ".".join(filename.split(".")[:-1])
    res = call("../parser/Elastic d " + filename + " " + new_path + " z", shell=True)
    if (res != 0):
        print("Error")
    call("rm " + filename, shell=True)
    return new_path


def recover_file(filename, dic):
    if filename.endswith("str"):
        arr = load_str_array(filename)
    elif filename.endswith("diff"):
        arr = load_int_array(filename)
        arr = recover_diff(arr)
        arr = arr.astype(str)
    elif filename.endswith("dat"):
        arr = load_int_array(filename)
    elif filename.endswith("var_dict"):
        arr = load_int_array(filename)
        arr = recover_diff(arr)
        arr = recover_dict(arr, dic)
    return arr
    
    
def recover_pat_bak(pat, values):
    new_value = {}
    cur_idx = 0
    new_idx = 0
    while cur_idx < len(values):
        # if the current index is in the pattern
        length = len(values[cur_idx])
        buf = ["" for _ in range(length)]
        while str(cur_idx) in pat:
            cur_value = values[cur_idx]
            buf = [buf[t] + str(cur_value[t]) + pat[str(cur_idx)] for t in range(length)]
            cur_idx += 1
        if cur_idx < len(values):
            buf = [buf[t] + str(values[cur_idx][t]) for t in range(length)]
        new_value[new_idx] = buf
        cur_idx += 1
        new_idx += 1
    return new_value

def recover_pat(pat, values):
    new_value = {}
    cur_idx = 0
    val_idx = 0
    while cur_idx < len(values):
        length = len(values[cur_idx])
        if str(val_idx) in pat:
            buf = ["" for _ in range(length)]
            cur_pat = pat[str(val_idx)]
            pos = 0
            for i in range(0, len(cur_pat[1])):
                buf = [str(buf[t]) + str(values[cur_idx][t]) + cur_pat[2][pos:pos+cur_pat[1][i]] for t in range(length)]
                pos += cur_pat[1][i]
                # if cur pattern is not the last one
                cur_idx += 1
            if len(cur_pat[1]) < cur_pat[0]:
                buf = [str(buf[t]) + str(values[cur_idx][t]) for t in range(length)]
                cur_idx += 1
        else:
            buf = values[cur_idx]
            cur_idx += 1
        new_value[val_idx] = buf
        val_idx += 1
    
    # import pdb; pdb.set_trace()
    return new_value
                
            
    