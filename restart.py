import sys
from time import sleep
import subprocess
import os

sleep(10)

command = ["nohup","python3","main.py","&"]
proc = subprocess.Popen(command)
proc.communicate()

args = sys.argv[1]
print(args)