import sys
import os
import shutil
import numpy as np

def mkdir(target_dir: str):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)


def list_write(file_path, li, append=False):
    print("Outputing " + file_path)
    if (append):
        fw = open(file_path, 'a')
    else:
        fw = open(file_path, "w")
    for i in li:
        fw.write(str(i).strip() + "\n")
    fw.close()
    
    
def isnumeric(array):
    try:
        # array.astype(int)
        array.astype(int)
        return True
    except:
        return False
    # return np.char.isnumeric(array).all()


def np_groupby(col, var):
    temp = set(col)
    results = {}
    for i in range(len(temp)):
        idx = np.where(col==temp[i])[0]
        results[temp[i]] = var[idx]
    return results
