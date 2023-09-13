
import time
import subprocess
import os
import sys
import argparse
import pickle

from compression.compress import *
from analyzer.property_miner import *
from preprocess import *
from utils.metrics import *
from utils.Logger import *
from utils.util_code import *
from utils.config import Config
from python_compression.sampler.clustering_sampling import *
from LogMeta import LogMeta

sys.path.append("../")

def run(
    input_file="",
    compress_outdir="",
    template_path="",
    ds="",
    compressed_fn="",
    sample_rate=0.1,
    threshold=0.1,
    n_candidate=128,
    h=50,
    re_mode=True,
    encode_mode=True,
    column_mode=True,
    seq_sampling=False,
    kernel='lzma',
    parsing=True,
    random_sam=False,
    mt=0.5,
    n_workers=4,
):
    # 1. preprocessing
    
    print("step 2: preprocessing... ")
    log_meta, log_seqs = preprocess(input_file=input_file,
                                    outdir=compress_outdir,
                                    ds=ds,
                                    template_path=template_path,
                                    h=h)
    # 2. simple preprocessing based on dictionary/common prefix

    if re_mode and log_meta.length > h:
        relations = property_mining(log_seqs=log_seqs,
                        log_meta=log_meta,
                        threshold=threshold, 
                        sample_rate=sample_rate, 
                        n_candidates=n_candidate,
                        h=h, 
                        sampling=seq_sampling,
                        random_sam=random_sam,
                        parsing=parsing,
                        mt=mt
                        )
    else:
        relations =  {
        'hdiff': [], 
        'pdiff': {}, 
        'hdict': [], 
        'pdict': {}, 
        'h_pat': {}, 
        'v_pat': {}
        }
        for eid, param in log_meta.param_list.items():
            res = np.array([isnumeric(x) for x in param])
            log_meta.num_col[eid] = np.where(res==True)[0]

       
    # 4. compression
    print("step 5: compressing... ")
    compress(log_meta,
            relations=relations,
            outdir=compress_outdir,
            compressed_fn=compressed_fn,
            encode_mode=encode_mode,
            column_mode=column_mode,
            var_min=re_mode,
            kernel=kernel
        )
    
