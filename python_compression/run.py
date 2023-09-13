
import time
import subprocess
import os
import sys
import argparse
import pickle
from subprocess import call
import argparse
import time
import datetime
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


# from compression.dictionary_encoding import *
from compression.compress import *
from preprocess import *
from utils.metrics import *
from utils.Logger import *
from utils.util_code import *
from utils.config import Config
from python_compression.sampler.clustering_sampling import *
import logshrink
lock = threading.RLock()
gl_threadTotTime = 0
gl_errorNum = 0

sys.path.append("../")


def add_arguments(argparser):
    argparser.add_argument("-ds",
                           default=None,
                           type=str,
                           required=True,
                           help="Dataset name")

    argparser.add_argument("-E",
                           default='E',
                           type=str,
                           help="Encode mode")
    argparser.add_argument("-C",
                           action='store_true',
                           help="column mode")
    argparser.add_argument("-Dict_c",
                           action='store_true',
                           help="Dict column mode")

    argparser.add_argument("-P",
                           action='store_true',
                           help="parsing")

    argparser.add_argument("-R",
                           action='store_true',
                           help="random sampling")

    argparser.add_argument("-DI",
                           action='store_true',
                           help="diff")

    argparser.add_argument("-V",
                           action='store_true',
                           help="variable extraction")

    argparser.add_argument("-S",
                           action='store_true',
                           help="sequence sampling")

    argparser.add_argument("-I",
                           type=str,
                           help="indir")

    argparser.add_argument("-K",
                           type=str,
                           help="kernel")

    argparser.add_argument("-L",
                           type=int,
                           default='5',
                           help="header length")

    argparser.add_argument("-NC",
                           type=int,
                           default='64',
                           help="sampling candidate")

    argparser.add_argument("-TN",
                           type=int,
                           default='4',
                           help="number of workers")

    argparser.add_argument("-wh",
                           type=int,
                           default='20',
                           help="windows length")

    argparser.add_argument("-th",
                           type=int,
                           default='5',
                           help="clustering distance threshold")

    argparser.add_argument("-outdir",
                           default='./out',
                           type=str,
                           help="out dir")

    argparser.add_argument("-mt",
                           type=float,
                           default='0.5',
                           help="multiplicity threshold")


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


def procFiles_result(future):
    atomic_addTime(future.result())


def threadsToExecTasks(ds, files, now_input, now_output, now_temp, type_template):
    fileListLen = len(files)
    curFileNumBegin = 0
    curFileNumEnd = 0
    step = maxSingleThreadProcFilesNum
    if (step == 0):  # dynamic step
        step = fileListLen // maxThreadNum
        if (step == 0):
            step = 1  # make sure the step is bigger than 0
    # import pdb; pdb.set_trace()
    threadPool = ThreadPoolExecutor(
        max_workers=maxThreadNum, thread_name_prefix="LS_")
    while curFileNumBegin < fileListLen:
        if (curFileNumBegin + step > fileListLen):
            curFileNumEnd = fileListLen - 1
        else:
            curFileNumEnd = curFileNumBegin + step - 1

        future = threadPool.submit(procFiles, ds, curFileNumBegin,
                                   curFileNumEnd, now_input, now_output, now_temp, type_template)
        future.add_done_callback(procFiles_result)
        curFileNumBegin = curFileNumEnd + 1

    # wait(future, return_when=ALL_COMPLETED)
    threadPool.shutdown(wait=True)


def procFiles(typename, fileBeginNo, fileEndNo, now_input, now_output, now_temp, type_template):
    t1 = time.time()
    thread_name = threading.current_thread().name
    now_temp += thread_name + "/"
    if not os.path.exists(now_temp):
        os.makedirs(now_temp)

    for i in range(fileBeginNo, fileEndNo + 1):
        print("Processing file: {} {}".format(now_temp, i))
        # run logshrink
        logshrink.run(
            input_file=os.path.join(now_input, str(i) + '.col'),
            compress_outdir=os.path.join(now_temp, str(i)),
            template_path=type_template,
            ds=ds,
            compressed_fn=str(i) + "_ls" + suffix,
            sample_rate=sample_rate,
            threshold=threshold,
            n_candidate=n_candidate,
            h=h,
            re_mode=re_mode,
            parsing=parsing,
            encode_mode=encode_mode,
            column_mode=column_mode,
            kernel=kernel,
            seq_sampling=seq_sampling,
            random_sam=random_sam,
            mt=mt
        )

    t2 = time.time()
    tempStr = "thread:{}, type:{}, fileNo: {} to {} , cost time: {}".format(
        threading.current_thread().name, typename, fileBeginNo, fileEndNo, t2 - t1)
    print(tempStr)

    return t2 - t1


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    add_arguments(argparser)
    args = argparser.parse_args()

    ds = args.ds
    encode_mode = args.E
    column_mode = args.C
    parsing = args.P
    random_sam = args.R
    re_mode = args.V
    header_length = args.L
    maxThreadNum = args.TN
    kernel = args.K
    seq_sampling = args.S
    n_candidate = args.NC
    h = args.wh
    threshold = args.th
    mt = args.mt

    # log_file = args.log_file
    segmenting = True
    sample_rate = 0.1
    blockSize = 100000
    maxSingleThreadProcFilesNum = 1
    # seq_sampling = True

    input_dir = args.I

    out_dir = args.outdir
    log_file = "_".join(['E', str(encode_mode), 'C', str(column_mode),
                        'R', str(random_sam), 'P', str(parsing),
                         'V', str(re_mode), 'K', kernel, 'S', str(
                             seq_sampling),
                         'H', str(h), 'TH', str(threshold), 'NC', str(n_candidate), 'mt', str(mt), '.log'])

    # test
    log_parser = "Drain"
    input_file = (input_dir +
                  ds + "/" + ds + ".log")

    compressed_fn = "logshrink"
    if kernel == 'lzma':
        suffix = ".7z"
    elif kernel == 'gzip':
        suffix = ".tar.gz"
    elif kernel == 'bz2':
        suffix = ".tar.bz2"
    template_path = os.path.join("./template", ds)

    compress_outdir = os.path.join(out_dir, ds)
    compressed_file = os.path.join(compress_outdir, compressed_fn + suffix)

    config_log_file(log_file)

    log("info", "==============================Processing dataset %s===========================================" % ds)

    log("info", "ARGS: encode mode: {}, column mode: {}".format(
        encode_mode, column_mode))
    t1 = time.time()
    mkdir(compress_outdir)

    # training
    template_path += '/'
    print("Step 1: segmenting...")
    seg_path = os.path.join(input_dir, ds, ds + "_Segment/")

    if segmenting:
        mkdir(template_path)
        train_cmd = "python3 ./parser/training.py -I " + input_file + \
            " -T " + template_path + " -L " + str(header_length)
        os.system(train_cmd)

        # segmenting
        mkdir(seg_path)
        f = open(input_file, encoding="ISO-8859-1")
        cou = 0
        count = 0
        buffer = []
        while True:
            line = f.readline()
            if not line:
                list_write(os.path.join(
                    seg_path, str(cou) + ".col"), buffer, True)
                break

            buffer.append(line)
            count += 1

            if count == blockSize:
                count = 0
                list_write(os.path.join(
                    seg_path, str(cou) + ".col"), buffer, True)
                buffer = []
                cou += 1

    time_t1 = time.time()
    print("Segmenting finished. ")
    all_files = os.listdir(seg_path)
    temp_path = os.path.join(compress_outdir, "tmp/")
    mkdir(temp_path)

    now_input_dir = seg_path

    mkdir(compress_outdir)

    print("Step2: Segmenting finished. ")
    # ThreadPool to Proc Files
    threadsToExecTasks(ds, all_files, now_input_dir,
                       compress_outdir, temp_path, template_path)

    # test
    # procFiles(ds, 0, len(all_files) - 1, now_input_dir,
    #   compress_outdir, temp_path, template_path)

    cmd = "mv {}*/*{} {}".format(temp_path, suffix, compress_outdir)
    print(cmd)
    os.system(cmd)
    time_t2 = time.time()

    print("{} finished, total time cost: {} , thread accum time: {}".format(
        compress_outdir, time_t2 - time_t1, gl_threadTotTime))
    gl_threadTotTime = 0  # reset

    time2 = time.time()

    print("{} Main finished, total time cost: {} , error num: {}".format(
        compress_outdir, time2 - time_t1, gl_errorNum))

    os.system("rm -rf {} ".format(temp_path))

    compression_speed = compress_speed(input_file, time2 - time_t1)
    cr = calculate_compression_ratio_path(input_file, compress_outdir)
    log("info", "%s Compression ratio %.3f, compression speed %.3f" %
        (ds, cr, compression_speed))
    print("%s Compression ratio %.3f, compression speed %.3f" %
          (ds, cr, compression_speed))
