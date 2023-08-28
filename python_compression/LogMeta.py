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
    
    def __init__(self, headers=None, eids=None, var_list=None):
        self.ori_eids = eids
        self.headers = headers
        self.header_num_str_split()
        # self.df = pd.concat([eids, var_list], axis=1)
        # self.df.columns = ['id', 'var']
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
        mapping = {idx: i for i, idx in enumerate(event_ids)}
        self.eids = np.array(list(map(lambda x: mapping[x], self.eids)))
        
    def split_var_list(self):
        self.num_col = {}
        self.str_col = {}
        self.param_list = {}
        for i in range(self.template_num):
            id_idx = np.where(self.eids==i)[0]
            param = np.array(self.var_list[id_idx].tolist()).T
            self.param_list[i] = param
            
            # res_table = self.split_str_num(param)
            # self.num_col[i] = np.where(res_table==True)[0]
            # self.str_col[i] = np.where(res_table==False)[0]
        
    def header_num_str_split(self):
        header_arr = self.headers.T.astype(str)
        # res_table = self.split_str_num(header_arr)
        self.headers = header_arr
        # self.header_num_col = np.where(res_table==True)[0]
        # self.header_str_col = np.where(res_table==False)[0]
        # self.header_num = self.headers[:,self.header_num_col].T
        # self.header_str = self.headers[:,self.header_str_col].T
        
    
    def split_str_num(self, array=None):
        # num: True, str: False
        res = np.array([isnumeric(x) for x in array])
        return res
    
    
    
        
    
    
    
            
        