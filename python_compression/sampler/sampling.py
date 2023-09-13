# Copyright refers to: https://github.com/LogIntelligence/LogPPT/blob/master/logppt/sampling/__init__.py
from utils.Logger import *
import random

from tqdm import tqdm
import numpy as np
from scipy.spatial.distance import cdist, pdist
import sys
sys.path.append("../")


def random_sampling(input_data=None, sample_rate=0.1):
    """ do randomly sampling from a large input_data with given sample_rate.

    Args:
    --------
    input_data: input large data matrix to be sampled.
    sample_rate: float number, e.g., 0.1 represents 10 is selected out of 100 data instances.

    Returns:
    --------
    sample_data: the sampled data
    """
    m = int(len(input_data) * sample_rate)
    # m = 60
    if m > 100:
        m = 100
    elif m <= 0:
        m = 1

    sample_ids = sorted(random.sample(range(len(input_data)), m))
    sample_data = []
    start = 0
    for i, line in enumerate(input_data):
        if start < len(sample_ids) and i == sample_ids[start]:
            start += 1
            sample_data.append(line)

    sample_data = np.array(sample_data)
    log("debug",
        'Step 1. Sampling with sample_rate %.3f, the original data size is %d, after sampling, the data size is %d'
        % (sample_rate, input_data.shape[0], sample_data.shape[0]))
    return sample_ids, sample_data


def random_sampling_seq(input_data=None, n_candidate=64):
    """ do randomly sampling from a large input_data with given sample_rate.

    Args:
    --------
    input_data: input large data matrix to be sampled.
    sample_rate: float number, e.g., 0.1 represents 10 is selected out of 100 data instances.

    Returns:
    --------
    sample_data: the sampled data
    """

    sample_ids = sorted(random.sample(range(len(input_data)), n_candidate))
    sample_data = []
    start = 0
    for i, line in enumerate(input_data):
        if start < len(sample_ids) and i == sample_ids[start]:
            start += 1
            sample_data.append(line)

    sample_data = np.array(sample_data)
    return sample_data
