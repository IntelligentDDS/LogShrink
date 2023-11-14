# LogShrink: An Effective Log Compression Tool

The repository is the implementation of paper in ICSE 2024 (early) "LogShrink: Effective Log Compression by Leveraging Commonality and Variability of Log Data". [Preprint Paper](https://arxiv.org/abs/2309.09479)

By Xiaoyun Li, Hongyu Zhang, Van-Hoang Le, Pengfei Chen


### Abstract
As systems grow in scale, log data generation has become increasingly explosive, leading to an expensive overhead on log storage, such as several petabytes per day in production. To address this issue, log compression has become a crucial task in reducing disk storage while allowing for further log analysis. We have conducted the empirical study on the characteristics of log data and obtained three major observations. Based on these observations, we propose LogShrink, a novel and effective log compression method by leveraging commonality and variability of log data. Please refer to the paper for more details.

![The overview of LogShrink](https://github.com/IntelligentDDS/LogShrink/blob/main/figures/framework.jpg)

### Dataset
We use 16 representative log datasets from [loghub](https://zenodo.org/record/3227177).The details of the dataset is shown as belows:

|    System types     | software system | File Size |      # Line |
| :-----------------: | :-------------: | :-------: | ----------: |
| Distributed systems |      HDFS       |  1.47GB   |  11,175,629 |
|                     |     Hadoop      |  48.61MB  |     394,308 |
|                     |      Spark      |  2.75GB   |  33,236,604 |
|                     |    Zookeeper    |  9.95MB   |      74,380 |
|                     |    OpenStack    |  58.61MB  |     207,820 |
|   supercomputers    |       BGL       | 708.76MB  |   4,747,963 |
|                     |       HPC       |  32.00MB  |     433,489 |
|                     |   Thunderbird   |  29.60GB  | 211,212,192 |
|  operating systems  |     Windows     |  26.09GB  | 114,608,388 |
|                     |      Linux      |  2.25MB   |      25,567 |
|                     |       Mac       |  16.09MB  |     117,283 |
|   mobile systems    |     Android     | 183.37MB  |   1,555,005 |
|                     |    HealthApp    |  22.44MB  |     253,395 |
| server applications |     Apache      |  4.90MB   |      56,481 |
|                     |     OpenSSH     |  70.02MB  |     655,146 |
| standalone software |    Proxifier    |  2.42MB   |      21,329 |

### How to run it
#### Environment Requirements
- python >=3.8
- gcc>=9.4.0
- 7zip, https://www.7-zip.org/download.html

Python package requirements can be installed by `pip install -r requirements.txt`


#### Run demo

- Example of LogShrink on Linux with LZMA zip tool:
```console
# compile log parser
cd python_compression/parser
make 

# run the compression part given a series of paramters. 
cd ..
python3 run.py -I ../test_logs/ -ds Linux -E E -C -K lzma -V -P -wh 50 -th 10 -NC 16 -S -outdir ./out/out -T ./templates
```
- The corresponding decompression command:
```
# run the decompression part given a series of parameters
cd decompression
python3 decompress_run.py -E E -K lzma -I ../out/out/Linux/ -T ../template/ -O ./restore_results
```
- More explanations of parameters:
  
```
python3 run.py -h
python3 decompression_run.py -h
```


### Experimental Results
We show the overall performance of LogShrink here.
#### The overall compression ratio of LogShrink

|   dataset   |  gzip  |  lzma   | zstd    | bzip2  | logzip  | LogReducer | LogShrink |
| :---------: | :----: | :-----: | ------- | ------ | :-----: | :--------: | :-------: |
|   Android   | 7.742  | 18.857  | 12.806  | 12.787 | 25.165  |   20.776   |  21.857   |
|   Apache    | 21.308 | 25.186  | 19.027  | 29.557 | 30.375  |   43.028   |  55.940   |
|     BGL     | 12.927 | 17.637  | 10.654  | 15.461 | 32.655  |   38.600   |  42.385   |
|   Hadoop    | 20.485 | 36.095  | 26.555  | 32.598 | 35.008  |   52.830   |  60.091   |
|    HDFS     | 10.636 | 13.559  | 10.368  | 14.059 | 16.666  |   22.634   |  27.319   |
|  HealthApp  | 10.957 | 13.431  | 9.999   | 13.843 | 22.632  |   31.694   |  39.072   |
|     HPC     | 11.263 | 15.076  | 9.858   | 12.756 | 27.208  |   32.070   |  35.878   |
|    Linux    | 11.232 | 16.677  | 12.293  | 14.695 | 23.368  |   25.213   |  29.252   |
|     Mac     | 11.733 | 22.159  | 17.143  | 18.074 | 26.306  |   35.251   |  39.860   |
|   OpenSSH   | 16.828 | 18.918  | 14.339  | 22.865 | 42.606  |   86.699   |  103.175  |
|  OpenStack  | 12.158 | 14.437  | 12.197  | 15.231 | 17.258  |   16.701   |  22.157   |
|  Proxifier  | 15.716 | 18.982  | 13.695  | 23.619 | 21.493  |   25.501   |  27.029   |
|    Spark    | 17.825 | 19.908  | 15.321  | 26.497 | 20.825  |   57.135   |  59.739   |
| Thunderbird | 16.462 | 27.309  | 19.112  | 25.428 |   ---   |   49.185   |  48.434   |
|   Windows   | 17.798 | 202.568 | 151.705 | 67.533 | 310.596 |  342.975   |  456.301  |
|  Zookeeper  | 25.979 | 27.667  | 23.134  | 36.156 | 47.373  |   94.562   |  116.981  |


#### The overall compression speed of LogShrink
|             | logzip | LogReducer | LogShrink |
| ----------- | :----: | :--------: | :-------: |
| Android     | 0.068  |   8.918    |   5.347   |
| Apache      | 0.737  |   1.686    |   1.880   |
| BGL         | 0.874  |   18.189   |   2.519   |
| Hadoop      | 0.901  |   4.919    |   3.137   |
| HDFS        | 0.701  |   20.570   |   3.253   |
| HealthApp   | 0.736  |   4.108    |   2.064   |
| HPC         | 0.644  |   5.110    |   2.485   |
| Linux       | 0.687  |   0.526    |   1.307   |
| Mac         | 0.009  |   2.887    |   2.572   |
| OpenSSH     | 0.715  |   13.268   |   3.409   |
| OpenStack   | 0.537  |   6.389    |   2.945   |
| Proxifier   | 0.716  |   0.929    |   1.315   |
| Spark       | 0.550  |   18.871   |   2.821   |
| Thunderbird |  ---   |   19.532   |   4.069   |
| Windows     | 1.357  |   31.938   |   5.507   |
| Zookeeper   | 0.842  |   3.071    |   2.523   |


### Citation
If you find the code and models useful for your research, please cite the following paper:

```
@inproceedings{li2023logshrink,
  title={LogShrink: Effective Log Compression by Leveraging Commonality and Variability of Log Data},
  author={Li, Xiaoyun and Zhang, Hongyu and Le, Van-Hoang and Chen, Pengfei},
  booktitle={2024 IEEE/ACM 46th International Conference on Software Engineering (ICSE)},
  pages={243--254},
  year={2023},
  organization={IEEE Computer Society}
}
```
