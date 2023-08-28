# Copyright refers to: https://github.com/LogIntelligence/LogPPT/blob/master/logppt/sampling/__init__.py

from Levenshtein import distance
from tqdm import tqdm
import numpy as np
import time

from pattern_extraction.sampling import *
from pattern_extraction.iterative_clustering import *


def clustering_sampling(seqs=None, threshold=0.1, sample_rate=0.01, template_num=0, n_candidates=128):
    # 1. iterative log sequence clustering  with given threshold
    # 2. sample balanced data
    
    t1 = time.time()
    cids, centers = iterative_clustering_seq(seqs, 
                                             sample_rate=sample_rate, 
                                             threshold=threshold, templates_number=template_num)
    sequence_num = len(centers)
    print(sequence_num)
    if sequence_num == 0:
        n_seq_candidate = 0
    else:
        n_seq_candidate = np.ceil(n_candidates / sequence_num)
    print(n_seq_candidate)
    sampled_seq = {}
    
    for i in range(sequence_num):
        sampled_index = np.random.choice(cids[i], int(n_seq_candidate))
        sampled_seq[i] = sampled_index
    
    print("clustering_sampling takes %.3f s"% (time.time() - t1))
    return sampled_seq #, centers


def adaptive_sampling(seqs=None, threshold=0.1, sample_rate=0.01, template_num=0, n_candidates=128):
    # 1. iterative log sequence clustering  with given threshold
    # 2. sample balanced data
    
    t1 = time.time()
    cids, centers = iterative_clustering_seq(seqs, 
                                             sample_rate=sample_rate, 
                                             threshold=threshold, templates_number=template_num)
    sequence_num = len(centers)
    print(sequence_num)
    n_seq_candidate = np.ceil(n_candidates / sequence_num)
    print(n_seq_candidate)
    sampled_seq = {}
    
    for i in range(sequence_num):
        sampled_index = np.random.choice(cids[i], int(n_seq_candidate))
        sampled_seq[i] = sampled_index
    
    print("clustering_sampling takes %.3f s"% (time.time() - t1))
    return sampled_seq, centers
    
