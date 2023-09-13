import os
import sys

sys.path.append("../../")
from benchmark.baselines import *
from python_compression.utils.metrics import *
import pandas as pd
from python_compression.utils.config import Config

# systems = ['Andriod_2k', 'Apache_2k', 'BGL_2k',  'Hadoop_2k', 'HDFS_2k', 'HealthApp_2k', 'HPC_2k', 'Linux_2k', 'Mac_2k', 'OpenSSH_2k', 'OpenStack_2k', 'Proxifier_2k', 'Spark_2k', 'Thunderbird_2k',  'Windows_2k', 'Zookeeper_2k']

# systems = ['Hadoop']

systems = ['Android', 'Apache', 'BGL', 'Hadoop', 'HealthApp', 'HPC',
    'Linux', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 
    'Zookeeper'
]
# systems = ['Spark']

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

if __name__ == '__main__':
    indir = '../../../log_collections/loghub'
    outdir = './'
    os.makedirs(outdir, exist_ok=True)
    suffix = '.tar.lr'
    print("====================LogReducer testing=================")
    running_results = []
    epoch = 1
    for i in range(epoch):
        print(f"**** Epoch {i + 1} ****")
        results = dict()
        for system in systems:
            current_dir = os.getcwd()
            input_filepath = os.path.join(indir, system, system + '.log')
            output_filepath = os.path.join(outdir, system + suffix)
            template_filepath = input_filepath + '_templates.csv'
            compress(system=system, compress_option='logreducer', filepath=input_filepath, output_dir=output_filepath,
                     template_filepath=template_filepath,
                     log_format=Config.drain_config[system.split('_')[0]]['log_format'],
                     header_length=header_length[system])
            results[system] = calculate_compression_ratio_path(input_filepath, f"../../benchmark/LogReducer/{output_filepath}")
            print("%s Compression ratio: \t\t %.3f" % (system, results[system]))
            os.chdir(current_dir)

        results_df = pd.Series(results, name='logreducer')
        running_results.append(results_df)
    final_results = pd.concat(running_results, axis=1)
    final_results['avg'] = final_results.mean(axis=1)

    final_results.to_csv('../../results/logreducer.csv')
    print(final_results)