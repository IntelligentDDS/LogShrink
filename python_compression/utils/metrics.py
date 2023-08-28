import argparse
from genericpath import getsize
import os
from difflib import SequenceMatcher

def loss_ratio(file_A, file_B):

    if not os.path.exists(file_A) or not os.path.exists(file_B):
        print("There is no path to compare")
        exit()

    score = 0
    total_line = 0

    with open(file_A, encoding="ISO-8859-1", errors="ignore") as A, open(file_B, encoding="ISO-8859-1", errors="ignore") as B:
        while True:
            a, b = A.readline(), B.readline()
            if not a:
                break
            score += SequenceMatcher(None, a, b).ratio()
            total_line += 1
    print("Read Lines: {0}".format(total_line))
    print("Lossless Score : {:.2f} %".format((score/total_line)*100))



def calculate_compression_ratio(file_A, file_B):
    if not os.path.exists(file_A) or not os.path.exists(file_B):
        print("There is no path to compare")
        # exit(1)
        return 0

    return os.path.getsize(file_A) / os.path.getsize(file_B)

def calculate_compression_ratio_path(file_A, file_B):
    print(file_B)
    if not os.path.exists(file_A) or not os.path.exists(file_B):
        print("There is no path to compare")
        exit()

    return os.path.getsize(file_A) / getdirsize(file_B)

def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(os.path.join(root, name)) for name in files])
    return size


def compress_speed(input_file, time_cost):
    return os.path.getsize(input_file) / time_cost

def decompress_speed(input_file, time_cost):
    return os.path.getsize(input_file) / time_cost

def evaluate(original, compressed, recover, compress_time, decompress_time):
    cr = calculate_compression_ratio(original, compressed)
    lr = loss_ratio(original, recover)
    cs = compress_speed(original, compress_time)
    ds = decompress_speed(compressed, decompress_time)

    return (cr, lr, cs, ds)
