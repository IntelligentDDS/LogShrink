#!/usr/bin/env python
# -*- coding: utf-8 -*-
# adapt from logreducer
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
import time
import datetime
import threading
import logging
from subprocess import call
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED  
from os.path import join, getsize

sys.path.append("../")
from utils import util_code



lock = threading.RLock()
gl_threadTotTime = 0
gl_errorNum = 0


#return exec time (t2-t1)
def procFiles(typename, fileBeginNo, fileEndNo, now_input, now_output, now_temp, type_template, suffix):
    t1 = time.time()
    #parser
    thread_temp = os.path.join(now_temp, threading.current_thread().name  + "/")
    if (os.path.exists(thread_temp)):
        call("rm -rf " + thread_temp)
    os.mkdir(thread_temp)    
    for t in range(fileBeginNo, fileEndNo+1):
        order = "python3 ./restore.py -I " + os.path.join(now_input,str(t)+suffix) + " -O " + os.path.join(now_output,str(t)+".col") + " -T " + type_template + " -t " + thread_temp + " -K " + kernel
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

def threadsToExecTasks(typename, files, now_input, now_output, now_temp, type_template, suffix):
    fileListLen = len(files)
    curFileNumBegin = 0
    curFileNumEnd = 0
    step = maxSingleThreadProcFilesNum
    if (step == 0):# dynamic step
        step = (fileListLen // maxThreadNum) + 1
        if(step == 0):
            step = 1 # make sure the step is bigger than 0
    
    threadPool = ThreadPoolExecutor(max_workers = maxThreadNum, thread_name_prefix="LS_")
    while curFileNumBegin < fileListLen:
        if (curFileNumBegin + step > fileListLen):
            curFileNumEnd = fileListLen - 1
        else:
            curFileNumEnd = curFileNumBegin + step - 1

        future = threadPool.submit(procFiles, typename, curFileNumBegin, curFileNumEnd, now_input, now_output, now_temp, type_template, suffix)
        future.add_done_callback(procFiles_result)
        curFileNumBegin = curFileNumEnd + 1
    #wait(future, return_when=ALL_COMPLETED)
    threadPool.shutdown(wait=True)


def add_arguments(argparser):
    argparser.add_argument("-E",
                           default='E',
                           type=str,
                           help="Encode mode")
    
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
    
    argparser.add_argument("-O",
                           default='./out',
                           type=str,
                           help="out dir")
    
    argparser.add_argument("-TN",
                           default=4,
                           type=int,
                           help="max thread num")

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
    
    template_path = args.T
    output_path = args.O
    mode = args.E
    kernel = args.K
    maxThreadNum = int(args.TN)
    maxSingleThreadProcFilesNum = 1
    blockSize = 100000
    #threadPool = ThreadPoolExecutor(max_workers = maxThreadNum, thread_name_prefix="test_")
    time1 = time.time()
    all_files = []
    
    if kernel == 'lzma':
        suffix = ".7z"
    elif kernel == 'gzip':
        suffix = ".tar.gz"
    elif kernel == 'bz2':
        suffix = ".tar.bz2"
        
    for f in os.listdir(input_path):
        try:
            if (f.endswith(suffix)):
                all_files.append(f)
        except:
            continue
    
    dataset = input_path.split("/")[-2]


    now_input = input_path
    now_output = os.path.join(output_path, dataset)
    util_code.mkdir(now_output)

    now_temp = os.path.join(now_output,"tmp/")
    if (not os.path.exists(now_temp)):
        pass
    else:
        call("rm -rf " + now_temp, shell=True)
    os.mkdir(now_temp)

    template_path = os.path.join(template_path, dataset)
    print(len(all_files))
    # threadsToExecTasks(dataset, all_files, now_input, now_output, now_temp, template_path, suffix)
    procFiles(dataset, 0, len(all_files)-1, now_input, now_output, now_temp, template_path, suffix)
     
    time_t1 = time.time()
        
    time_t2 = time.time()
    tempStr = "{} finished, total time cost: {} , thread accum time: {}".format(now_output, time_t2 - time_t1, gl_threadTotTime)
    print(tempStr)
    gl_threadTotTime = 0 # reset

    time2 = time.time() 
    tempStr = "{} Main finished, total time cost: {} , error num: {}".format(output_path, time2 - time1, gl_errorNum)
    print(tempStr)
    call("rm -rf " + now_temp, shell=True)

   


