#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import random
import textdistance
from Levenshtein import distance
from itertools import tee, islice
# use a cython implementation of ts distance
import sys

def LCS(seq1, seq2):
    lengths = [[0 for j in range(len(seq2)+1)] for i in range(len(seq1)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            if seq1[i] == seq2[j]:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])

    # read the substring out from the matrix
    # backtracking
    result = []
    lenOfSeq1, lenOfSeq2 = len(seq1), len(seq2)
    while lenOfSeq1!=0 and lenOfSeq2 != 0:
        if lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1-1][lenOfSeq2]:
            lenOfSeq1 -= 1
            result.insert(0, '<*>')
        elif lengths[lenOfSeq1][lenOfSeq2] == lengths[lenOfSeq1][lenOfSeq2-1]:
            lenOfSeq2 -= 1
            result.insert(0, '<*>')
        else:
            assert seq1[lenOfSeq1-1] == seq2[lenOfSeq2-1]
            result.insert(0,seq1[lenOfSeq1-1])
            lenOfSeq1 -= 1
            lenOfSeq2 -= 1
    if lenOfSeq1 or lenOfSeq2:
        result.insert(0, '<*>')
    return lengths[len(seq1)][len(seq2)], result



def lcs_distance(x, y):
    seq1 = x.split()
    seq2 = y.split()
    lengths = [[0 for j in range(len(seq2) + 1)] for i in range(len(seq1) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            if seq1[i] == seq2[j]:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j],
                                            lengths[i][j + 1])

    return 1 - 2 * lengths[-1][-1] / (len(seq1) + len(seq2))


def min_distance(c_set, t_set):
    D = []
    for c_inst in c_set:
        min_candidate_distance = 1e10
        for t_inst in t_set:
            min_candidate_distance = min(min_candidate_distance,
                                         lev_distance(t_inst, c_inst))
        D.append(min_candidate_distance)
    return D

def lev_distance(seq1, seq2):
    return distance(seq1, seq2)

def lcs_distance(seq1, seq2):
    length, res = LCS(seq1, seq2)
    return 1 - length / len(seq1)

def euclidean(seq1, seq2):
    dist = np.linalg.norm(seq1-seq2) / len(seq1)
    return dist

def mix_distance(seq1, seq2):
    return (lcs_distance(seq1, seq2) + euclidean(seq1, seq2)) / 2

# 2 times faster than original ngram
def ngram(iterable, n=2):
    return zip(*(islice(it, pos, None) for pos, it in enumerate(tee(iterable, n))))

def diff_ngram_sim(sa, sb):
    sim = 1 - (len(sa) + len(sb) - 2 * len(np.intersect1d(sa, sb))) / (len(sa) + len(sb))
    return sim

def diff_ngram(sent_a, sent_b, num):
    a = ngram(sent_a, num)
    b = ngram(sent_b, num) 
    sa = set(tuple(i) for i in a)
    sb = set(tuple(i) for i in b)
    sim = (len(sa) + len(sb) - 2 * len(sa.intersection(sb))) / (len(sa) + len(sb))
    return sim

def ngram_1_distance(seq1, seq2):
    return diff_ngram(seq1, seq2, 1)

def ngram_2_distance(seq1, seq2):
    return diff_ngram(seq1, seq2, 2)

def ngram_3_distance(seq1, seq2):
    return diff_ngram(seq1, seq2, 3)

def lev_distance(x, y):
    return textdistance.levenshtein.normalized_distance(x, y)


def euc_distance(x, y):
    return textdistance.cosine.normalized_distance(x[0], y[0])

def entropy_distance(x, y):
    return textdistance.entropy_ncd.normalized_distance(x[0], y[0])


def jaccard_distance(x, y):
    return textdistance.jaccard.normalized_distance(x.split(), y.split())


def ratcliff_distance(x, y):
    return textdistance.ratcliff_obershelp.normalized_distance(x, y)