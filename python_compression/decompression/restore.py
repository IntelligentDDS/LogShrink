# adapt from logreducer https://github.com/THUBear-wjy/LogReducer


import argparse
from collections import defaultdict
import re
import os
import time
import sys
import json
from subprocess import call


from decompress import *
sys.path.append("../")

from utils import util_code

splitregex = re.compile(r'(\s+|:|<\*>|,|=)')


def load_tempaltes(template_path):
    Template_file = open(template_path,encoding="ISO-8859-1")
    Template_lines = Template_file.readlines()
    Templates = {}
    Index = {}
    now_template = []
    now_index = []
    first = True
    for line in Template_lines:
        if (re.search('\[\d+\]\\n',line) and len(line) < 10):
            num = int(line[1:-2])
            if (num == 0):
                continue
            Templates[num] = now_template
            Index[num] = now_index
            now_template = []
            now_index = []
            first = True
            continue
        
        if (first):
            first = False
        else:
            now_template.append('\n')
        for n, s in enumerate(splitregex.split(line.strip())):
            if (s == "<*>"):
                # store the variable index
                now_index.append(n)
            now_template.append(s)
    return Templates, Index


def get_info(head_path):
    #Head length 9
    #is multiple 1
    #Head regex "\d{4}-\d{2}-\d{2}"
    #Head type map dict[0] = [1, 0], dict[7] = [6,7]
    #Head format map dict[0] = "%s", dict[7] = "%d-%d-%d-%d.%d.%d.%d"
    #Head string length dict[0] = [-1], dict[7] = [1,1,1,1,1,1]
    #Head number length dict[0] = [], dict[7] = [4,2,2,2,2,2,6]
    #Head delimer []
    fo = open(head_path, 'r')
    headLength = int(fo.readline().strip())
    isMulti = int(fo.readline().strip())
    if isMulti == 1:
        headRegex = fo.readline().strip()
    else:
        headRegex = None
    headType = dict()
    headFormat = dict()
    headString = []
    headNumber = []
    headDelimer = []
    for i in range(0, headLength):
        parts = fo.readline().strip().split()
        headType[i] = [int(parts[0]), int(parts[1])]
        headFormat[i] = parts[2]
        if (headType[i][0] == 1 and headType[i][1] == 0): #only string
            headNumber.append(-1)
            continue
        for t in range(0, headType[i][0]):
            headString.append(int(parts[3 + t]))
        for t in range(0, headType[i][1]):
            headNumber.append(int(parts[3 + headType[i][0] + t]))
    for i in range(0, headLength):
        headDelimer.append(fo.readline()[0:-1])
    return headLength, isMulti, headRegex, headType, headFormat, headString, headNumber, headDelimer
    
    
def restore_elastic_encoder(path, suffixs):
    for file in os.listdir(path):
        for suffix in suffixs:
            if file.endswith(suffix):
                new_path = elastic_decoder(filename=os.path.join(path, file))
                
    

def restore_heads(path, tempalte_path, relations):

    def getValue(dic):
        headValue = {}
        files = [file for file in os.listdir(path) if re.search(r'head_var_col\d+.', file)]
        files = sorted(files)
        for i in range(0, len(files)):
            curValue = recover_file(os.path.join(path, files[i]), dic)
            headValue[i] = curValue
        return headValue
    
    def pending(num, length):
        if length == -1:
            return str(num)
        else:
            temp = str(num)
            while len(temp) < length:
                temp = "0" + temp
            return temp
        
    headLength, isMulti, headRegex, headType, headFormat, headString, headNumber, headDelimer = get_info(os.path.join(template_path, "head.format"))
    # print(headType)
    
    HeadDict = load_dict(os.path.join(path,"header.dict"))
    tmpValue = getValue(HeadDict)
    # concatenate patterns
    HeadValue = recover_pat(relations['h_pat'], tmpValue)
    
    totLength = len(HeadValue[0])
    for key in HeadValue.keys():
        assert(len(HeadValue[key]) == totLength)
    now_num = 0
    now_str = 0
    Heads = ["" for i in range(0, totLength)]
    #Restore each part
    for i in range(0, headLength):
        if (headType[i][0] == 1 and headType[i][1] == 0):
            Heads = [Heads[t] + HeadValue[now_num][t] + headDelimer[i] for t in range(0, totLength)]
            now_num += 1
            continue
        now_format = headFormat[i]
        fidx = 0
        while fidx < len(now_format):
            if (now_format[fidx] == '%' and now_format[fidx+1] == 'd'): #Num
                try:
                    Heads = [Heads[t] + pending(HeadValue[now_num][t], headNumber[now_num]) for t in range(0, totLength)]
                except:
                    print("now_num:{}, len(headValue):{}, len(Heads):{}, len(headValue):{}, tot_length:{}, len(headNumber): {}".format(now_num, len(HeadValue), len(Heads),len(HeadValue[now_num]), totLength, len(headNumber)))
                    exit(-1)
                now_num += 1
                fidx += 2
            else: #String start
                Heads = [Heads[t] + now_format[fidx] for t in range(0, totLength)]
                fidx += 1
        Heads = [Heads[t] + headDelimer[i] for t in range(0, totLength)]
    return Heads, [isMulti, headRegex]    

def restore_variables(path, relations): #Restore varibales for each template
    var_list = defaultdict(dict)
    # build dict
    var_dict = load_dict(os.path.join(path, "var.dict"))
    
    # get file list
    files = [f for f in os.listdir(path) if re.search(r'var_list_', f)]
    files = sorted(files)
    # import pdb; pdb.set_trace()
    for f in files:
        var = recover_file(os.path.join(path, f), var_dict)
        id_res = re.search(r'var_list_E(\d+)_(\d+)', f)
        tid = int(id_res.group(1))
        vid = int(id_res.group(2))
        var_list[tid][vid] = var
    # concatenate from relations
    for tid in var_list.keys():
        var_list[tid] = recover_pat(relations['v_pat'][str(tid)], var_list[tid])
    # import pdb; pdb.set_trace()
    return var_list
        
    


def load_log(path, head_msg):
    Logs = []
    if (head_msg[0] == 1): #Is multiline
        headregex = re.compile(head_msg[1])
    lines = load_str_array_raw(path)
    
    now_line = ""
    start = True 
    
    for lined in lines:
        if (head_msg[0] != 1 or headregex.search(lined)):
            if (start):
                start = False
                now_line = lined.strip()
                continue
            
            Logs.append(now_line)
            now_line = lined.strip()
        else:
            if (start):
                Logs.append(lined.strip())
                continue
            if (lined == "\n"):
                Logs.append(now_line)
                Logs.append(lined.strip())
                start = True
                continue
            
            now_line += '\n' + lined.strip()
        
    Logs.append(now_line)
    return Logs


if __name__ == "__main__":
    #Target, success restore 0-D-Z state
    parser = argparse.ArgumentParser()
    parser.add_argument("--Input", "-I", help="The input compressed file")
    parser.add_argument("--Kernel", "-K", help="The kernel of the zip tool")
    parser.add_argument("--Output", "-O", default="./restore_result/", help="The output path of the restored log file")
    parser.add_argument("--Template", "-T",  help="The template path")
    parser.add_argument("--Temp", "-t", default="./temp/", help="The temp output path")
    args = parser.parse_args()

    template_path = args.Template
    input_path = args.Input
    output_path = args.Output
    temp_path = args.Temp
    kernel = args.Kernel

    # output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0])
    util_code.mkdir(temp_path)
    # util_code.mkdir(output_path)
    
    # Load templates
    Templates, Index = load_tempaltes(os.path.join(template_path, "template.col"))    
    
    # 1. Use unzip tool to extract all files
    unzip_tool(kernel=kernel, input_file=input_path, output_dir=temp_path)   
    
    # 2. Restore compresseed files by leveraging commonality and variability  
    relations = load_relations(relation_file=os.path.join(temp_path, "relations"))
    
    # print(relations)
    # 3. restore elastic code
    restore_elastic_encoder(path=temp_path, suffixs=['ee'])
    
    
    # 4. Restore Head
    Heads, head_msg = restore_heads(path=temp_path, tempalte_path=template_path, relations=relations)
    
    # 5. Restore individual templates variables
    var_list = restore_variables(path=temp_path, relations=relations)
    
    #6. Load load_failed log
    LoadFailed = load_log(os.path.join(temp_path, "load_failed.log"), head_msg)
    
    #7. Load match_failed log
    MatchFailed = load_log(os.path.join(temp_path, "match_failed.log"), head_msg)
    
    print("Load failed #: {}, Match failed #:{}".format(len(LoadFailed), len(MatchFailed)))
    #Use Eid, load_failed, match_failed, Tempaltes, Index, Variables
    match_idx = 0
    load_idx = 0
    head_idx = 0
    template_idx = defaultdict(lambda: 0)

    Eids = load_int_array(os.path.join(temp_path,"eids.eid"))
    
    eids_len = len(Eids)
    assert eids_len == len(LoadFailed) + len(MatchFailed) + len(Heads)
    
    fw = open(output_path, "wb")
    for eid in Eids:
        # load failed
        if eid == -1:
            fw.write((LoadFailed[load_idx] + '\n').encode())
            load_idx += 1
            continue
        # match failed
        if eid == 0:
            fw.write((MatchFailed[match_idx] + '\n').encode())
            match_idx += 1
            continue
        
        # normal parsing result
        head = Heads[head_idx]
        head_idx += 1
        template = Templates[eid]
        variables = var_list[eid]
        now_idx = template_idx[eid]
        now_var = 0
        buf = head

        # fill blank inline
        for s in template:
            if (s == "<*>"):
                buf += str(variables[now_var][now_idx])
                now_var += 1
            else:
                buf += s
        
        fw.write((buf + '\n').encode())
        template_idx[eid] += 1
    assert eids_len == head_idx + load_idx + match_idx
    fw.close()
    #Clean up
    call("rm -rf " + temp_path, shell=True)
