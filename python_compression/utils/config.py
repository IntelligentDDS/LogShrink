import os
import sys


class Config:
    # window length
    h: 50
    drain_config = {
        'HDFS': {
            'log_file': 'HDFS/HDFS_2k.log',
            'log_format': '<Date> <Time> <Pid> <Level> <Component>: <Content>',
            'regex': [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'],
            'st': 0.5,
            'depth': 4
        },
        'Hadoop': {
            'log_file': 'Hadoop/Hadoop_2k.log',
            # 'log_format': '<Date> <Time> <Level> \[<Process>\] <Component>: <Content>',
            'log_format':
            '<Year>-<Month>-<Day> <Hour>:<Min>:<Sec>,<mSec> <Level> \[<Process>\] <Component>: <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Spark': {
            'log_file': 'Spark/Spark_2k.log',
            # 'log_format': '<Date> <Time> <Level> <Component>: <Content>',
            'log_format':
            '<Day>/<Month>/<Year> <Hour>:<min>:<sec> <Level> <Component>: <Content>',
            'regex':
            [r'(\d+\.){3}\d+', r'\b[KGTM]?B\b', r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.5,
            'depth': 4
        },
        'Zookeeper': {
            'log_file': 'Zookeeper/Zookeeper_2k.log',
            'log_format':
            '<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>',
            # '<Year>-<Month>-<Day> <Hour>:<Min>:<Sec>,<mSec> - <Level>  \[<node>\] - <Content>',
            'regex': [r'(/|)(\d+\.){3}\d+(:\d+)?'],
            'st': 0.5,
            'depth': 4
        },
        'BGL': {
            'log_file': 'BGL/BGL_2k.log',
            # 'log_format': '<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>',
            'log_format':
            '<Label> <Timestamp> <Year>\.<Mon>\.<D> <Node> <Yearr>-<Month>-<Day>-<Hour>\.<Min>\.<Sec>\.<mSec> <NodeRepeat> <Type> <Component> <Level> <Content>',
            'regex': [r'core\.\d+'],
            'st': 0.5,
            'depth': 4
        },
        'HPC': {
            'log_file': 'HPC/HPC_2k.log',
            'log_format':
            # '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>',
            '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>',
            'regex': [r'=\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Thunderbird': {
            'log_file': 'Thunderbird/Thunderbird_2k.log',
            'log_format':
            '<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Windows': {
            'log_file': 'Windows/Windows_2k.log',
            'log_format':
            '<Date> <Time>, <Level>                  <Component>    <Content>',
            'regex': [r'0x.*?\s'],
            'st': 0.7,
            'depth': 5
        },
        'Linux': {
            'log_file': 'Linux/Linux_2k.log',
            'log_format':
            # '<Month> <Date> <Time> <Level> <Component>: <Content>',
            '<Month> <Date> <Y>:<m>:<s> <Level> <Component>: <Content>',
            'regex': [r'(\d+\.){3}\d+', r'\d{2}:\d{2}:\d{2}'],
            'st': 0.39,
            'depth': 6
        },
        'Android': {
            'log_file':
            'Andriod/Andriod_2k.log',
            'log_format':
            # '<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>',
            '<mon>-<day> <hour>:<min>:<sec>\.<msec>  <Pid>  <Tid> <Level> <Component>: <Content>',

            'regex': [
                r'(/[\w-]+)+', r'([\w-]+\.){2,}[\w-]+',
                r'\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b'
            ],
            'st':
            0.2,
            'depth':
            6
        },
        'HealthApp': {
            'log_file': 'HealthApp/HealthApp_2k.log',
            # 'log_format': '<Time>\|<Component>\|<Pid>\|<Content>',
            'log_format':
            '<date>-<hour>:<min>:<sec>:<msec>\|<Component>\|<Pid>\|<Content>',
            'regex': [],
            'st': 0.2,
            'depth': 4
        },
        'Apache': {
            'log_file': 'Apache/Apache_2k.log',
            # 'log_format': '\[<Time>\] \[<Level>\] <Content>',
            'log_format':
            '\[<date> <mon> <day> <hour>:<min>:<sec> <year>\] \[<Level>\] <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Proxifier': {
            'log_file':
            'Proxifier/Proxifier_2k.log',
            # 'log_format': '\[<Time>\] <Program> - <Content>',
            'log_format':
            '\[<Month>.<Day> <Hour>:<Min>:<Sec>\] <Program> - <Content>',
            'regex': [
                r'<\d+\ssec', r'([\w-]+\.)+[\w-]+(:\d+)?',
                r'\d{2}:\d{2}(:\d{2})*', r'[KGTM]B'
            ],
            'st':
            0.6,
            'depth':
            3
        },
        'OpenSSH': {
            'log_file': 'OpenSSH/OpenSSH_2k.log',
            # 'log_format': '<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>',
            'log_format':
            '<Date> <Day> <Hour>:<Min>:<Sec> <Component> sshd\[<Pid>\]: <Content>',
            'regex': [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.6,
            'depth': 5
        },
        'OpenStack': {
            'log_file': 'OpenStack/OpenStack_2k.log',
            'log_format':
            '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>',
            'regex': [r'((\d+\.){3}\d+,?)+', r'/.+?\s', r'\d+'],
            'st': 0.5,
            'depth': 5
        },
        'Mac': {
            'log_file': 'Mac/Mac_2k.log',
            'log_format':
            # '<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>',
            '<Month>  <Date> <H>:<M>:<S> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>',
            'regex': [r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.7,
            'depth': 6
        },
    }

    drain_config_bak = {
        'HDFS': {
            'log_file': 'HDFS/HDFS_2k.log',
            'log_format': '<Date> <Time> <Pid> <Level> <Component>: <Content>',
            'regex': [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'],
            'st': 0.5,
            'depth': 4
        },
        'Hadoop': {
            'log_file': 'Hadoop/Hadoop_2k.log',
            'log_format':
            '<Date> <Time> <Level> \[<Process>\] <Component>: <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Spark': {
            'log_file': 'Spark/Spark_2k.log',
            'log_format': '<Date> <Time> <Level> <Component>: <Content>',
            'regex':
            [r'(\d+\.){3}\d+', r'\b[KGTM]?B\b', r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.5,
            'depth': 4
        },
        'Zookeeper': {
            'log_file': 'Zookeeper/Zookeeper_2k.log',
            'log_format':
            '<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>',
            'regex': [r'(/|)(\d+\.){3}\d+(:\d+)?'],
            'st': 0.5,
            'depth': 4
        },
        'BGL': {
            'log_file': 'BGL/BGL_2k.log',
            'log_format':
            '<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>',
            'regex': [r'core\.\d+'],
            'st': 0.5,
            'depth': 4
        },
        'HPC': {
            'log_file': 'HPC/HPC_2k.log',
            'log_format':
            '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>',
            'regex': [r'=\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Thunderbird': {
            'log_file': 'Thunderbird/Thunderbird_2k.log',
            'log_format':
            '<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Windows': {
            'log_file': 'Windows/Windows_2k.log',
            'log_format':
            '<Date> <Time>, <Level>                  <Component>    <Content>',
            'regex': [r'0x.*?\s'],
            'st': 0.7,
            'depth': 5
        },
        'Linux': {
            'log_file': 'Linux/Linux_2k.log',
            'log_format':
            '<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>',
            'regex': [r'(\d+\.){3}\d+', r'\d{2}:\d{2}:\d{2}'],
            'st': 0.39,
            'depth': 6
        },
        'Andriod': {
            'log_file':
            'Andriod/Andriod_2k.log',
            'log_format':
            '<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>',
            'regex': [
                r'(/[\w-]+)+', r'([\w-]+\.){2,}[\w-]+',
                r'\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b'
            ],
            'st':
            0.2,
            'depth':
            6
        },
        'HealthApp': {
            'log_file': 'HealthApp/HealthApp_2k.log',
            'log_format': '<Time>\|<Component>\|<Pid>\|<Content>',
            'regex': [],
            'st': 0.2,
            'depth': 4
        },
        'Apache': {
            'log_file': 'Apache/Apache_2k.log',
            'log_format': '\[<Time>\] \[<Level>\] <Content>',
            'regex': [r'(\d+\.){3}\d+'],
            'st': 0.5,
            'depth': 4
        },
        'Proxifier': {
            'log_file':
            'Proxifier/Proxifier_2k.log',
            'log_format':
            '\[<Time>\] <Program> - <Content>',
            'regex': [
                r'<\d+\ssec', r'([\w-]+\.)+[\w-]+(:\d+)?',
                r'\d{2}:\d{2}(:\d{2})*', r'[KGTM]B'
            ],
            'st':
            0.6,
            'depth':
            3
        },
        'OpenSSH': {
            'log_file': 'OpenSSH/OpenSSH_2k.log',
            'log_format':
            '<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>',
            'regex': [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.6,
            'depth': 5
        },
        'OpenStack': {
            'log_file': 'OpenStack/OpenStack_2k.log',
            'log_format':
            '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>',
            'regex': [r'((\d+\.){3}\d+,?)+', r'/.+?\s', r'\d+'],
            'st': 0.5,
            'depth': 5
        },
        'Mac': {
            'log_file': 'Mac/Mac_2k.log',
            'log_format':
            '<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>',
            'regex': [r'([\w-]+\.){2,}[\w-]+'],
            'st': 0.7,
            'depth': 6
        },
    }
