import os
import argparse
import time
from datetime import datetime
import sys

def clean(trash_path, age_thr, log_file):
    now = time.time()
    for root, dirs, files in os.walk(trash_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            last_changes = os.path.getmtime(file_path)
            if (now - last_changes) > age_thr:
                try:
                    os.remove(file_path)
                    log_file.write(f"{datetime.now()} [FILE] {file_path}\n")
                except OSError as e:
                    log_file.write(f"{datetime.now()} [ERROR] {e}\n")
        
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
                log_file.write(f"{datetime.now()} [DIR] {dir_path}\n")
            except OSError:
                pass

parser = argparse.ArgumentParser()
parser.add_argument('--trash_folder_path', required=True)
parser.add_argument('--age_thr', type=int, required=True)
args = parser.parse_args()

if not os.path.isdir(args.trash_folder_path):
    print(f"Error: Directory {args.trash_folder_path} does not exist")
    sys.exit(1)

with open("clean_trash.log", "a") as log_file:
    while True:
        clean(args.trash_folder_path, args.age_thr, log_file)
        log_file.flush()
        time.sleep(1)
