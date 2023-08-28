import logging
import os

def log(level, msg, *args):
    if level == 'info':
        logging.info(msg, *args)
    
def config_log_file(filename):
    output_dir = "./running_record/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logging.basicConfig(filename=output_dir + filename, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
