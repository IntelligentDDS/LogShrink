import pandas as pd
import numpy as np
import subprocess
import os
import sys
from tqdm import tqdm
import pickle as pkl
import time
import re
import ast
from datetime import datetime
import multiprocessing as mp
from subprocess import call

sys.path.append('../')
from utils.config import Config
from utils.Logger import *
from utils.util_code import *
from LogMeta import LogMeta
# from LogCompression.backup.calculate_diff import *

def lr_log_parsing(
                input_path="",
                outdir="",
                template_path=""):
    
    print("step 2.1: log parsing... {}".format(input_path))

    filename = input_path.split("/")[-1].split('.')[0]
    input_dir = os.path.dirname(input_path)
    input_dir += '/'
    outdir += '/'
    print(outdir)
    parsing_cmd = "./parser/THULR -I " + input_dir + " -X " + filename + " -O " + outdir + " -T " + template_path + " -E " + " -D " + " -F " + os.path.join(template_path, "head.format")
    print(parsing_cmd)
    res = call(parsing_cmd,shell=True)
    

def read_parsing_result(input_dir="",
                ds="",
                template_path=""):
    
    print("Step 2.2, log matching, parsing file: %s" % input_dir)
    t1 = time.time()
    header_list = []
    files = [i for i in os.listdir(input_dir) if i.endswith("head")]
    files = sorted(files)
    for i in files:
        header = read_col(os.path.join(input_dir, i))
        header_list.append(header)
        del header
            
    header_df = pd.concat(header_list, axis=1)
    eids_df, df_var = read_var(os.path.join(input_dir, "var.var"))
    log_meta = LogMeta(headers=header_df.values, eids=eids_df.values, var_list=df_var.values)

    del eids_df, df_var, header_df
        
    log("info", "log parsing took %.3f s, parsing into %d templates" %
          (time.time() - t1, log_meta.template_num))
    
    return log_meta



def read_col(filename: str):
    ids = []
    with open(filename, "r") as f:
        for line in f.readlines():
            ids.append(line.strip())  
    return pd.Series(ids)



def read_var(filename: str):
    # parameter_lists = pd.read_csv(filename, sep=",")
    parameter_lists = []
    eids = []
    with open(filename, "r") as f:
        for line in f.readlines():            
            parse_list = line.strip().split("||")
            eids.append(parse_list[0])
            parameter_lists.append(parse_list[1:-1])
    return pd.Series(eids).astype(int), pd.Series(parameter_lists)


def get_logsequence(series: pd.Series, h=50):
    print("Step 2.3, get log sequence list")

    sequences_list = []
    i = 0
    for i in range(int(np.floor(series.shape[0] / h))):
        sequences_list.append(series[i * h:(i + 1) * h].tolist())
    # TODO: handling the last window
    last = series[(i + 1) * h:].tolist()
    last.extend([-1] * (h - len(last)))
    sequences_list.append(last)
    sequences_list = np.array(sequences_list)

    log("info", "Total length is %d, cut into %d sequences" %
          (series.shape[0], len(sequences_list)))

    return sequences_list

# def get_diff_df(df: pd.DataFrame()):
#     if df.shape[0] == 0 or df.shape[1] == 0:
#         return df
#     df = df.astype(int)
#     diff = np.diff(df, axis=1)
#     diff = np.hstack((df[:,0].reshape(-1,1), diff))
#     diff = diff.astype(int)
#     return diff


def log_parsing(
    input_file=None,
    outdir="",
    ds="",
    template_path="",
    fileNo=-1
):
    results = {}
    for idx, file in enumerate(input_file):
        temp_dir = os.path.join(outdir, str(fileNo[idx]) + 'temp')
        mkdir(temp_dir)
        lr_log_parsing(input_path=file, 
                    outdir=temp_dir, 
                    template_path=template_path)
        
    return results

def preprocess(
    input_file=None,
    outdir="",
    ds="",
    template_path="",
    h=50
):
    # 1. log parsing
    temp_dir = os.path.join(outdir, 'temp')
    mkdir(temp_dir)
    lr_log_parsing(input_path=input_file, 
                   outdir=temp_dir, 
                   template_path=template_path)
    # keep processing failed log
    os.system("mv {}/*failed.log {}".format(temp_dir, outdir))
    # 2. read parsing result
    log_meta = read_parsing_result(input_dir=temp_dir,
                ds=ds,
                template_path=template_path)
    # rm template dir
    shutil.rmtree(temp_dir)
    # 3. cut into fixed-length log sequences
    seq_list = get_logsequence(log_meta.eids, h=h)
    return log_meta, seq_list