#!/usr/bin/python
from subprocess import Popen

if __name__ == '__main__':
    Popen(['/home/storm/apache-storm-1.0.2/bin/storm', 'supervisor'])
    Popen(['/home/storm/apache-storm-1.0.2/bin/storm', 'logviewer'])
    print('success!')
