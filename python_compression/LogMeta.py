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
from subprocess import call

from utils.config import Config
from utils.Logger import *
from utils.util_code import *


class LogMeta(object):
    
    ori_eids = None
    headers = None
    header_str = None
    header_num = None
    header_str_e = {}
    header_num_e = {}
    eids = None
    var_list = None
    param_list = None
    length = 0
    mapping = {}
    
    def __init__(self, headers=None, eids=None, var_list=None):
        # import pdb; pdb.set_trace()
        self.ori_eids = eids
        self.headers = headers
        self.header_num_str_split()
        valid_index = np.where(eids>0)[0]
        self.eids = eids[valid_index]
        self.var_list = var_list[valid_index]
        
        self.rename_ids()
        self.template_num = len(set(self.eids))
        self.split_var_list()
        self.length = len(self.ori_eids)
        self.header_dict = {}
        self.var_dict = {}
        self.num_col = {}
        self.header_num = []
        

        
    def rename_ids(self):
        event_ids = set(self.eids)
        remap = {idx: i for i, idx in enumerate(event_ids)}
        self.mapping = {v: int(k) for k, v in remap.items()}
        self.eids = np.array(list(map(lambda x: remap[x], self.eids)))
        
    def split_var_list(self):
        self.num_col = {}
        self.str_col = {}
        self.param_list = {}
        for i in range(self.template_num):
            id_idx = np.where(self.eids==i)[0]
            param = np.array(self.var_list[id_idx].tolist()).T
            self.param_list[i] = param
            
        
    def header_num_str_split(self):
        header_arr = self.headers.T.astype(str)
        self.headers = header_arr
    
    def split_str_num(self, array=None):
        res = np.array([isnumeric(x) for x in array])
        return res
    
    
    
        
    
    
    
            
        