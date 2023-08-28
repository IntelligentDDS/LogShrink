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
import sys
import os
import argparse
import util
import time
import datetime
import threading
import logging
from subprocess import call
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED  
from os.path import join, getsize

sys.path.append("../")
from LogMeta import LogMeta



lock = threading.RLock()
gl_threadTotTime = 0
gl_errorNum = 0

# step 1:
# load all files
# reload elastic encoder file
# join all the content
# restore by the log template ID
# join the log template

#return exec time (t2-t1)
def procFiles(typename, fileBeginNo, fileEndNo, now_input, now_output, now_temp, type_template):
    t1 = time.time()
    #parser
    thread_temp = os.path.join(now_temp, threading.current_thread().name  + "/")
    if (os.path.exists(thread_temp)):
        call("rm -rf " + thread_temp)
    os.mkdir(thread_temp)    
    for t in range(fileBeginNo, fileEndNo+1):
        order = "python3 ./restore.py -I " + os.path.join(now_input,str(t)+".7z") + " -O " + os.path.join(now_temp,str(t)+".col") + " -T " + type_template + " -t " + thread_temp
        print(order + " " + threading.current_thread().name)
        res = call(order,shell=True)
        if (res != 0):
            tempStr = "Error Occur at: {} thread: {}, fileNo: {} to {}".format(typename, threading.current_thread().name, fileBeginNo, fileEndNo)
            print (tempStr)
            atomic_addErrnum(1)
            continue
    t2 = time.time()
    tempStr = "thread:{}, type:{}, fileNo: {} to {} , cost time: {}".format(threading.current_thread().name, typename, fileBeginNo, fileEndNo, t2 - t1)
    print (tempStr)
    
    return t2 - t1

def threadsToExecTasks(typename, files, now_input, now_output, now_temp, type_template):
    fileListLen = len(files)
    curFileNumBegin = 0
    curFileNumEnd = 0
    step = maxSingleThreadProcFilesNum
    if (step == 0):# dynamic step
        step = (fileListLen // maxThreadNum) + 1
        if(step == 0):
            step = 1 # make sure the step is bigger than 0
    
    threadPool = ThreadPoolExecutor(max_workers = maxThreadNum, thread_name_prefix="LR_")
    while curFileNumBegin < fileListLen:
        if (curFileNumBegin + step > fileListLen):
            curFileNumEnd = fileListLen - 1
        else:
            curFileNumEnd = curFileNumBegin + step - 1

        future = threadPool.submit(procFiles, typename, curFileNumBegin, curFileNumEnd, now_input, now_output, now_temp, type_template)
        future.add_done_callback(procFiles_result)
        curFileNumBegin = curFileNumEnd + 1
    #wait(future, return_when=ALL_COMPLETED)
    threadPool.shutdown(wait=True)


def add_arguments(argparser):
    argparser.add_argument("-E",
                           default='E',
                           type=str,
                           help="Encode mode")
    

    argparser.add_argument("-V",
                           action='store_true',
                           help="relation miner")
    
    argparser.add_argument("-K",
                           type=str,
                           help="kernel")
    
    
    argparser.add_argument("-I",
                           default='./out',
                           type=str,
                           help="input dir")
    
    argparser.add_argument("-T",
                           default='./template',
                           type=str,
                           help="template path")
    
    argparser.add_argument("-outdir",
                           default='./out',
                           type=str,
                           help="out dir")

def procFiles_result(future):
    atomic_addTime(future.result())

def atomic_addTime(step):
    lock.acquire()
    global gl_threadTotTime
    gl_threadTotTime += step
    lock.release()

def atomic_addErrnum(step):
    lock.acquire()
    global gl_errorNum
    gl_errorNum += step
    lock.release()

if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    add_arguments(parse)
    args = parse.parse_args()

    #init params
    input_path = args.I
    template_path = util.path_pro(args.T)
    output_path = args.Output
    time_diff = args.TimeDiff
    mode = args.Mode
    kernel = args.K
    maxThreadNum = int(args.MaxThreadNum)
    maxSingleThreadProcFilesNum = int(args.ProcFilesNum)
    blockSize = int(args.BlockSize)
    #threadPool = ThreadPoolExecutor(max_workers = maxThreadNum, thread_name_prefix="test_")
    time1 = time.time()
    all_files = []
    for f in os.listdir(input_path):
        try:
            if (f.split(".")[1] == "7z"):
                all_files.append(f)
        except:
            continue

    type_template = template_path
    
    filename = output_path.split("/")[-1]
    path = util.path_pro(output_path.split(filename)[0])
    print("filename: {}, path: {}".format(filename, path))

    now_input = input_path
    now_output = path
    if (not os.path.exists(path)):
        os.mkdir(path)

    now_temp = os.path.join(path,"tmp/")
    if (not os.path.exists(now_temp)):
        pass
    else:
        call("rm -rf " + now_temp, shell=True)
    os.mkdir(now_temp)

    now_type = filename.split(".")[0]
    print(len(all_files))
    threadsToExecTasks(now_type, all_files, now_input, now_output, now_temp, type_template)
   
     
    time_t1 = time.time()
        
    time_t2 = time.time()
    tempStr = "{} finished, total time cost: {} , thread accum time: {}".format(now_output, time_t2 - time_t1, gl_threadTotTime)
    print(tempStr)
    gl_threadTotTime = 0 # reset

    time2 = time.time() 
    tempStr = "{} Main finished, total time cost: {} , error num: {}".format(output_path, time2 - time1, gl_errorNum)
    print(tempStr)

   


