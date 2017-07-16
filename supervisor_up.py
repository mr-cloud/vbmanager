#!/usr/bin/python
from subprocess import Popen
import time


if __name__ == '__main__':
    Popen(['/home/storm/apache-storm-1.0.2/bin/storm', 'supervisor'])
    time.sleep(10)
    Popen(['/home/storm/apache-storm-1.0.2/bin/storm', 'logviewer'])
    time.sleep(10)
    print('success!')
