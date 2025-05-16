import os
import argparse
import re

def normal(pattern):
    pattern = pattern.strip()
    regex = re.escape(pattern).replace(r'\*', '.*') 
    return f'^{regex}$'

parser = argparse.ArgumentParser()
parser.add_argument('--project_dir', type=str, required=True)
args = parser.parse_args()
project_dir = args.project_dir
gitignore = os.path.join(project_dir, '.gitignore')
    
rule_1 = []
rule_2 = []
with open(gitignore, 'r') as f:
    for line in f:
        if line[0] == '*':
            regex = re.compile(normal(line))
            rule_2.append((line, regex))
        else:
            rule_1.append(line)

ignore_list = []    
for root, dirs, files in os.walk(project_dir):
    for file in files:
        long_way = os.path.join(root, file)
        short_way = os.path.relpath(long_way, project_dir)
        if short_way in rule_1:
            ignore_list.append((long_way, short_way))
            continue

        for pattern, regex in rule_2:
            if regex.match(short_way):
                ignore_list.append((long_way, pattern))

print("Ignored files:")
for path, reason in ignore_list:
    print(f"{path} ignored by expression {reason}")
