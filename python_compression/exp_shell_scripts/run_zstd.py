import sys
sys.path.append("../../")
from benchmark.baselines import *
from python_compression.utils.metrics import *
import pandas as pd

# systems = ['Andriod_2k', 'Apache_2k', 'BGL_2k',  'Hadoop_2k', 'HDFS_2k', 'HealthApp_2k', 'HPC_2k', 'Linux_2k', 'Mac_2k', 'OpenSSH_2k', 'OpenStack_2k', 'Proxifier_2k', 'Spark_2k', 'Thunderbird_2k',  'Windows_2k', 'Zookeeper_2k']

systems = ['Apache']#, 'BGL',  'Hadoop', 'HDFS', 'HealthApp', 'HPC', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 'Spark', 'Zookeeper']

if __name__ == '__main__':
    indir = '../../log_collections/loghub'
    outdir = './compress_output'
    suffix = '.zst'
    results = dict()
    print("====================ZStandard testing=================")
    for system in systems:
        input_filepath = os.path.join(indir, system + '.log')
        output_filepath = os.path.join(outdir, system + suffix)
        compress(system=system, compress_option='zstd', filepath=input_filepath, output_dir=outdir)
        results[system] = calculate_compression_ratio(input_filepath, output_filepath)
        print("%s Compression ratio: \t\t %.3f" % (system, results[system]))

    results_df = pd.Series(results, name='zstd')
    
    results_df.to_csv('../../results/zstd.csv')

    