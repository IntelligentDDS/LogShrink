#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import random
import time
import os
import sys
from tqdm import tqdm
import pickle
import shutil
import tarfile
from io import BytesIO
sys.path.append("../")
from LogMeta import LogMeta



def compress(log_meta, relations: list,
                 outdir: str,
                 compressed_fn: str, 
                 encode_mode: str, 
                 column_mode: str, 
                 var_min: bool,
                 EE: bool,
                 EH: bool,
                 EV: bool,
                 HH: bool,
                 VV: bool,
                 kernel='lzma'
                 ):
    print("Compressing all files, including base, diff, id, and var list")
    
    output_csv(arr_list=log_meta.headers, num_col=log_meta.header_num, outdir=outdir, relations=relations,
                outfile="head_var_col", encode_mode=encode_mode, column_mode=column_mode)
    

    if var_min:
        output_relation(relations, outdir=outdir, outfile="relations", encode_mode=encode_mode)

    output_eids(log_meta.ori_eids, outdir=outdir, outfile="eids", encode_mode=encode_mode, column_mode=column_mode)
    output_var_list_bin(log_meta.eids, log_meta.param_list, log_meta.num_col, relations=relations, outdir=outdir, outfile="var_list", 
                            suffix=".var", encode_mode=encode_mode, column_mode=column_mode)
    output_dict(log_meta.header_dict, outdir, "header")
    
    output_dict(log_meta.var_dict, outdir, "var")
    packer(kernel=kernel, outdir=outdir, outfile=compressed_fn)
    
def output_dict(d, outdir="", outfile=""):
    with open(os.path.join(outdir, outfile + ".dict"), "w") as f:
        for key in sorted(d.keys(), key=d.get):
            f.write("{}\n".format(key))
            
def packer(kernel='lzma', outdir=None, outfile=""):
    # run once and check three kernels
    # running lzma
    files = os.listdir(outdir)
    if kernel == 'lzma':
        lzma_cmd = "7z a {} {} -m0=LZMA".format(os.path.join(outdir),
                                os.path.join(outdir, "*"))
        os.system(lzma_cmd)    
    elif kernel == "gzip":
        print(os.path.join(outdir, outfile))
        tar = tarfile.open(outdir + '.tar.gz', "w:gz", compresslevel=9)
        for f in os.listdir(outdir):
            tar.add(os.path.join(outdir, f), arcname=os.path.basename(f))
        tar.close()
    elif kernel == "bz2":
        print(os.path.join(outdir, outfile))
        tar = tarfile.open(outdir + '.tar.bz2', "w:bz2", compresslevel=9)
        for f in os.listdir(outdir):
            tar.add(os.path.join(outdir, f), arcname=os.path.basename(f))
        tar.close()     

def output_relation(relations: dict, outdir: str, outfile: str, encode_mode: str="E"):
    with open(os.path.join(outdir, outfile + '.hdiff'), 'w') as file:
        int_array_writer(file, relations['hdiff'])
    with open(os.path.join(outdir, outfile + '.hdict'), 'w') as file:
        int_array_writer(file, relations['hdict'])
        
    with open(os.path.join(outdir, outfile + '.pdiff'), 'w') as file:
        file.write("{}".format(relations['pdiff']))
    with open(os.path.join(outdir, outfile + '.pdict'), 'w') as file:
        file.write("{}".format(relations['pdict']))

    with open(os.path.join(outdir, outfile + '.h_pat'), 'w') as file:
        file.write("{}".format(relations['h_pat']))
    with open(os.path.join(outdir, outfile + '.p_pat'), 'w') as file:
        file.write("{}".format(relations['v_pat']))
        
        
def output_csv(arr_list: np.array, num_col, relations, outdir: str, outfile: str, encode_mode: str='E', column_mode: bool=True):
    # turn all int into bytes
    # import pdb; pdb.set_trace()
    if column_mode:
        for i, arr in enumerate(arr_list):
            if i in relations['hdiff']:
                with open(os.path.join(outdir, outfile + str(i) + ".diff"), get_filemode(encode_mode)) as file:
                    int_array_writer(file, arr.astype(int), encode_mode=encode_mode)
            elif i in relations['hdict']:
                with open(os.path.join(outdir, outfile + str(i) + ".var_dict"), get_filemode(encode_mode)) as file:
                    int_array_writer(file, arr.astype(int), encode_mode=encode_mode)
            elif i in num_col:
                with open(os.path.join(outdir, outfile + str(i) + ".dat"), get_filemode(encode_mode)) as file:
                    int_array_writer(file, arr.astype(int), encode_mode=encode_mode)
            else:
                with open(os.path.join(outdir, outfile + str(i) + ".str"), 'w') as file:
                    string_writer(file, arr)

    else:
        with open(os.path.join(outdir, outfile + ".base"), get_filemode(encode_mode)) as file:
            for i, arr in arr_list.items():
                if len(arr) > 0:
                    if type(arr[0]) is np.int64:
                        int_array_writer(file, arr, encode_mode)
                    else:
                        string_writer(file, arr)


def output_eids(arr_list: pd.Series, outdir: str, outfile: str, encode_mode: str="E", column_mode: bool=True):
    with open(os.path.join(outdir, outfile + ".eid"), get_filemode(encode_mode)) as file:
        int_array_writer(file, arr_list, encode_mode)
    
def string_writer(file, arr_list):
    for j in range(len(arr_list)):
        file.write("{}\n".format(arr_list[j]))
    

def int_array_writer(file, arr_list, encode_mode='NE', diff=False):
    base = 0
    for j in range(len(arr_list)):
        to_write = arr_list[j]
        if diff:
            to_write = arr_list[j] - base
            base = arr_list[j]
        int_writer(file, to_write, encode_mode)
            
def int_writer(file, num, encode_mode):
    # elastic encoding
    if encode_mode == 'E':
        if type(num) == np.int64:
            num = num.item()
        file.write(elastic_encoder(num))
    else:
        file.write("%d\n"%num)
        
def get_filemode(encode_mode: str):
    if encode_mode == 'NE':
        file_mode = 'w'
    else:
        file_mode = 'wb'
    return file_mode
        
    
    

def output_var_list_bin(eids, var, num_col, relations, outdir, outfile, suffix, encode_mode='E', column_mode=True):
    # TODO: too many hardcodes
    # log message parameter list
    if column_mode:
        for eid, arr_list in var.items():
            for i in range(len(arr_list)):
                if eid in relations['pdiff'] and i in relations['pdiff'][eid]:
                    with open(os.path.join(outdir, outfile + "_E" + str(eid) + "_" + str(i) + ".diff"), get_filemode(encode_mode)) as file:
                        int_array_writer(file, arr_list[i].astype(int), encode_mode=encode_mode)
                elif eid in relations['pdict'] and i in relations['pdict'][eid]:
                    with open(os.path.join(outdir, outfile + "_E" + str(eid) + "_" + str(i) +".var_dict"), get_filemode(encode_mode)) as file:
                        int_array_writer(file, arr_list[i].astype(int), encode_mode=encode_mode)
                elif eid in num_col and i in num_col[eid]:
                    with open(os.path.join(outdir, outfile + "_E" + str(eid) + "_" + str(i) +".dat"), get_filemode(encode_mode)) as file:
                        int_array_writer(file, arr_list[i].astype(int), encode_mode=encode_mode)
                else:
                    with open(os.path.join(outdir, outfile + "_E" + str(eid) + "_" + str(i) +".str"), 'w') as file:
                        string_writer(file, arr_list[i])

    else:
        for eid, arr_list in var.items():
            with open(os.path.join(outdir, outfile + "_E" + str(eid) + suffix), get_filemode(encode_mode)) as file:
                for arr in arr_list.T:
                    file.write("{}\n".format(arr.join(",")))

def string_encoder(data, file, column_mode=True):
    if column_mode:
        split_str = np.array(list(map(list, data))).T
        for c in split_str:
            for r in c:
                file.write("{}".format(r))
            file.write("\n")
    else:
        for c in data:
                file.write("{}\n".format(c))

        
def output_var_list_column( var, outdir, outfile, suffix, encode_mode='E', column_mode=True, 
                        dict_column_mode=True, diff=True):
    # TODO: too many hardcodes
    # log message parameter list
    if column_mode == 1:
        for eid, arr_list in var.items():
            with open(os.path.join(outdir, outfile + "_E" + str(eid) + suffix), get_filemode(encode_mode)) as file:
                for arr in arr_list:
                    for i in arr:
                        file.write("{}\n".format(i))
                    
    elif column_mode == 2:
        for eid, arr_list in var.items():
            with open(os.path.join(outdir, outfile + "_E" + str(eid) + suffix), get_filemode(encode_mode)) as file:
                for arr in arr_list.T:
                    file.write("{}\n".format("".join(arr.tolist())))
    else:
        for eid, arr_list in var.items():
            for i in range(len(arr_list)):
                with open(os.path.join(outdir, outfile + "_E" + str(eid) + "_" + str(i) + suffix), get_filemode(encode_mode)) as file:
                    for item in arr_list[i]:
                        file.write("{}\n".format(item))

                
def zigzag_encoder(num: int):
    return (num << 1) ^ (num >> 31)


def zigzag_decoder(num: int):
    return (num >> 1) ^ -(num & 1)



def elastic_encoder(num: int):
    # TODO: there're some bugs in elastic encoder
    buffer = b''
    cur = zigzag_encoder(num)
    for i in range(4):
        if (cur & (~0x7f)) == 0:
            buffer += cur.to_bytes(1, "big")
            # ret = i + 1
            break
        else:
            buffer += ((cur & 0x7f) | 0x80).to_bytes(1, 'big')
            cur = cur >> 7
    return buffer


def elastic_decoder(num):
    # TODO: there're some bugs in elastic encoder
    # when i > 2**28, there's a bug. 
    # buffer = b''
    ret = 0
    offset = 0
    i = 0
    
    while i < 5:
        cur = num[i]
        if (cur & (0x80) != 0x80):
            ret |= (cur << offset)
            i+=1
            break
        else:
            ret |= ((cur & 0x7f) << offset)
        i += 1
        offset += 7
            
    decode_num = zigzag_decoder(ret)
    return decode_num

def int_2_bytes(num: int) -> bytes:
    return num.to_bytes(4, 'big', signed=True)

def int_encoder(num: int, encode_mode='E'):
    if encode_mode == "E":
        return elastic_encoder(num)
    else:
        return int_2_bytes(num)
