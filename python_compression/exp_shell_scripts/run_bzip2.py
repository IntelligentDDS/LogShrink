import sys
sys.path.append("../../")
from benchmark.baselines import *
from python_compression.utils.metrics import *
import pandas as pd

# systems = ['Andriod', 'Apache', 'BGL',  'Hadoop', 'HDFS', 'HealthApp', 'HPC', 'Linux', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 'Spark', 'Thunderbird',  'Windows', 'Zookeeper']

systems = ['Apache']#, 'BGL',  'Hadoop', 'HDFS', 'HealthApp', 'HPC', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 'Spark', 'Zookeeper']

if __name__ == '__main__':
    indir = '../../log_collections/loghub'
    outdir = './compress_output'
    suffix = '.tar.bz2'
    results = dict()
    print("====================Bzip2 testing=================")
    for system in systems:
        input_filepath = os.path.join(indir, system + '.log')
        output_filepath = os.path.join(outdir, system + suffix)
        compress(system=system, compress_option='bzip2', filepath=input_filepath, output_dir=outdir)
        results[system] = calculate_compression_ratio(input_filepath, output_filepath)
        print("%s Compression ratio: \t\t %.3f" % (system, results[system]))

    results_df = pd.Series(results, name='bzip2')
    
    results_df.to_csv('../../results/bzip2.csv')

    