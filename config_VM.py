#!/usr/bin/python3
import sys
import os


if __name__ == '__main__':
    datanode_num = sys.argv[1]
    data = []
    filename = '/etc/network/interfaces'
    #filename = 'config_VM.test'
    with open(filename, 'r') as interfaces:
        for line in interfaces:	
            if line.startswith('address'):
                line = line.rstrip()
                words = line.split(' ')
                words[1] = '192.168.56.10' + str(datanode_num)
                line = words[0] + ' ' + words[1] + '\n'
            data.append(line)

    with open(filename, 'w') as interfaces:
        interfaces.writelines(data)			

    #filename = 'config_VM_hostname.test'
    filename = '/etc/hostname'
    with open(filename, 'w') as hostname:
        hostname.write('data' + str(datanode_num) + '\n')
    os.system('rm -rf /home/storm/datahouse/storm/storm-local/')
    print('success!')	


