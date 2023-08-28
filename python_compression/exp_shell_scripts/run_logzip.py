import sys
sys.path.append("../../")
from benchmark.baselines import *
from python_compression.utils.metrics import *
import pandas as pd
from projects.LogShrink.python_compression.utils.config import Config

# systems = ['Andriod_2k', 'Apache_2k', 'BGL_2k',  'Hadoop_2k', 'HDFS_2k', 'HealthApp_2k', 'HPC_2k', 'Linux_2k', 'Mac_2k', 'OpenSSH_2k', 'OpenStack_2k', 'Proxifier_2k', 'Spark_2k', 'Thunderbird_2k',  'Windows_2k', 'Zookeeper_2k']


systems = ['Apache', 'BGL',  'Hadoop', 'HDFS', 'HealthApp', 'HPC', 'Mac', 'OpenSSH', 'OpenStack', 'Proxifier', 'Zookeeper']
systems = ['Spark']

if __name__ == '__main__':
    indir = '~/Documents/Github/log_collections/loghub'
    templates_dir = '~/Documents/Github/logparser/benchmark/Drain_result'
    outdir = './compress_output'
    suffix = '.logzip.tar.bz2'
    results = dict()
    print("====================LogZip testing=================")
    for system in systems:
        input_filepath = os.path.join(indir, system, system + '.log')
        output_filepath = os.path.join(outdir, system + suffix)
        template_filepath = os.path.join(templates_dir, system + '.log_templates.csv')
        
        compress(system=system, compress_option='logzip', filepath=input_filepath, output_dir=outdir, \
                template_filepath=template_filepath, log_format=Config.drain_config[system.split('_')[0]]['log_format'])
        results[system] = calculate_compression_ratio(input_filepath, output_filepath)
        print("%s Compression ratio: \t\t %.3f" % (system, results[system]))

    results_df = pd.Series(results, name='logzip')
    
    results_df.to_csv('../../results/logzip.csv')

    