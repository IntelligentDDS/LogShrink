import os
import shutil
import tarfile
import glob
import re
import json
import sys
import subprocess

sys.path.append("../")
from benchmark.logzip.logzip.logzipper import Ziplog


# TODO: log block, log archieve, ELISE
def compress(system="", compress_option="", filepath="", template_filepath=None, log_format="", output_dir=None, header_length=4):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    # options: gzip, zstd, lzma, logzip, logreducer
    if compress_option == "gzip":
        compress_by_gzip(filepath, os.path.join(output_dir, system + ".tar.gz"))
    elif compress_option == "bzip2":
        compress_by_gzip(filepath, os.path.join(output_dir, system + ".tar.bz2"))
    elif compress_option == "zstd":
        compress_by_zstd(filepath, os.path.join(output_dir, system + ".zst"))
    elif compress_option == "lzma":
        compress_by_lzma(filepath, os.path.join(output_dir, system + ".tar.lz"))
    elif compress_option == "logzip":
        compress_by_LogZip(system, filepath, template_filepath, logformat=log_format, output_dir=output_dir)
    elif compress_option == "logreducer":
        compress_by_LogReducer(filepath, output_dir, header_length)


def compress_by_gzip(filepath, output_name):
    tar = tarfile.open(output_name, "w:gz", compresslevel=9)
    tar.add(filepath, arcname=os.path.basename(filepath))
    tar.close()


def compress_by_bzip2(filepath, output_name):
    tar = tarfile.open(output_name, "w:bz", compresslevel=9)
    tar.add(filepath, arcname=os.path.basename(filepath))
    tar.close()
    
    
def compress_by_zstd(filepath, output_name):
    cmd = "zstd " + filepath + " -f --ultra -o " + output_name
    os.system(cmd)

def compress_by_lzma(filepath, output_name):
    # change to 7z
    cmd = "7z a {} {}".format(output_name, filepath)
    os.system(cmd)


def compress_by_LogReducer(filepath, output_dir, header_length):
    # train 
    # compress
    train_cmd = "python3 ./training.py -I " + filepath + " -T ./template/ -L " + str(header_length) 
    compress_cmd = "python3 ./LogReducer.py -I " + filepath + " -T ./template/  -O " + output_dir

    current_dir = os.getcwd()
    os.chdir('../../benchmark/LogReducer')
    os.system(f"rm -rf ./template/ && rm -rf {output_dir}")
    os.system(train_cmd + " > /dev/null 2>&1")
    os.system(compress_cmd + " > /dev/null 2>&1")
    os.chdir(current_dir)


def compress_by_LogZip(system, filepath, templates_filepath, logformat, output_dir):
    tmp_dir = os.path.join("./tmp_dir", system)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    level = 1
    kernel = "bz2"   # options: (1) gz  (2) bz2
    zipper = Ziplog(logformat=logformat,
                    outdir=output_dir,
                    outname=system + '.logzip',
                    kernel=kernel,
                    tmp_dir=tmp_dir,
                    level=level)
    zipper.zip_file(filepath, templates_filepath)

