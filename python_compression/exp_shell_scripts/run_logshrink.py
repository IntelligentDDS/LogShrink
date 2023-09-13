import sys

sys.path.append("../")
from benchmark.baselines import *
from python_compression.utils.metrics import *
import pandas as pd

# systems = ['Andriod_2k', 'Apache_2k', 'BGL_2k',  'Hadoop_2k', 'HDFS_2k', 'HealthApp_2k', 'HPC_2k', 'Linux_2k', 'Mac_2k', 'OpenSSH_2k', 'OpenStack_2k', 'Proxifier_2k', 'Spark_2k', 'Thunderbird_2k',  'Windows_2k', 'Zookeeper_2k']

systems = [
    'Android', 'Apache', 'BGL', 'Hadoop', 'HDFS', 'HealthApp', 'HPC',
    'Linux', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 'Spark',
    'Zookeeper'
]

systems = ['Android', 'Apache', 'Hadoop', 'HealthApp', 'HPC',
    'Linux', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 
    'Zookeeper'
]
systems = ['Apache', 'Hadoop']
# systems = ["Android", "HDFS", "Spark"]

header_length = {
    'Android': 6,
    'Apache': 6,
    'BGL': 9,
    'Hadoop': 5,
    'HDFS': 5,
    'HealthApp': 3,
    'HPC': 6,
    'Linux': 5,
    'Mac': 5,
    'OpenSSH': 5,
    'OpenStack': 7,
    'Proxifier': 4,
    'Spark': 4,
    'Thunderbird': 9,
    'Windows': 4,
    'Zookeeper': 6
}


def add_arguments(argparser):
    argparser.add_argument("-E",
                           default='E',
                           type=str,
                           help="Encode mode")
    argparser.add_argument("-C",
                           action='store_true',
                           help="column mode")
    
    argparser.add_argument("-P",
                           action='store_true',
                           help="parsing")
    
    argparser.add_argument("-R",
                           action='store_true',
                           help="random sampling")
    

    argparser.add_argument("-V",
                           action='store_true',
                           help="relation miner")
    
    argparser.add_argument("-S",
                           action='store_true',
                           help="sequence sampling")
    
    
    argparser.add_argument("-K",
                           type=str,
                           help="kernel")
    
    argparser.add_argument("-L",
                           type=int,
                           default='5',
                           help="header length")
    
    
    argparser.add_argument("-NC",
                           type=int,
                           default='64',
                           help="sampling candidate")
    
    argparser.add_argument("-wh",
                           type=int,
                           default='20',
                           help="windows length")
    
    argparser.add_argument("-th",
                           type=int,
                           default='5',
                           help="clustering threshold")

    argparser.add_argument("-I",
                           default='./out',
                           type=str,
                           help="input dir")
    
    argparser.add_argument("-outdir",
                           default='./out',
                           type=str,
                           help="out dir")
    argparser.add_argument("-mt",
                           type=float,
                           default='0.5',
                           help="multiplicity threshold")


if __name__ == '__main__':
    suffix = '.7z'
    
    argparser = argparse.ArgumentParser()

    add_arguments(argparser)
    args = argparser.parse_args()
    
    encode_mode = args.E
    column_mode = args.C
    random_sam = args.R
    parsing = args.P
    variable_mining = args.V
    kernel = args.K
    sequence_sampling = args.S
    h = args.wh
    threshold = args.th
    n_candidates = args.NC
    mt = args.mt
    
    indir = args.I
    out_dir = args.outdir
    
    command = " -E " + encode_mode + " -K " + kernel + ' -wh ' + str(h) + " -th " + str(threshold) + " -NC " + str(n_candidates) + " -mt " + str(mt)
    out_dir += '_' + encode_mode + '_' + kernel + '_' + str(h) + '_' + str(threshold) + '_' + str(n_candidates) + "_" + str(mt)

    if column_mode:
        command += " -C "
        out_dir += '_C_'
    if random_sam:
        command += " -R "
        out_dir += '_R_'
    if parsing:
        command += " -P "
        out_dir += '_P_'
    if variable_mining:
        command += " -V "
        out_dir += '_V_'
    if sequence_sampling:
        command += " -S "
        out_dir += '_S_'
    outfile  = command
    
    command += " -I " + indir
    
    results = list()
    print("====================LogShrink Testing=================")
    
    epoch = 1
    
    for i in range(epoch):
        print(f"**** Epoch {i + 1} ****")
        epoch_res = dict()
        for system in systems: 
            print("====================%s=================" % system)

            input_filepath = os.path.join(indir, system, system + '.log')
            output_dir = os.path.join(out_dir, system)
            cmd = "python3 run.py -TN 8 -ds {} {} -outdir {} -L {}".format(system, command, out_dir, header_length[system])
            os.system(cmd)
            epoch_res[system] = calculate_compression_ratio_path(input_filepath,
                                                        output_dir)
            print("%s Compression ratio: \t\t %.3f" % (system, epoch_res[system]))

        results.append(pd.Series(epoch_res, name=f'R_{i}'))
        
    df = pd.concat(results, axis=1)
    df.to_csv('../results/logshrink_' + outfile + '.csv')
