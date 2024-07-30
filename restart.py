import sys
from time import sleep
import subprocess
import os

sleep(10)

command = ["nohup","python3","main.py","&"]
proc = subprocess.Popen(command)
proc.communicate()

kill = os.getpid()
command = ["kill","-KILL",f"{kill}"]
proc = subprocess.Popen(kill)
proc.communicate()

args = sys.argv[1]
print(args)