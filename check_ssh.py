#!/usr/bin/python -u

import socket
import sys
import argparse
import getpass
import time
import paramiko

def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0

def check_ssh(host, username, password, port=22, inital_wait=0, interval=0, retries=1):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    time.sleep(inital_wait)

    for x in range(retries):
        try:
            client.connect(hostname=host, port=port, username=username, password=password)
            client.close()
            return True
        except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.AuthenticationException,
                    paramiko.ssh_exception.SSHException, socket.error) as e:
            print e
            time.sleep(interval)

parser = argparse.ArgumentParser()

g2 = parser.add_mutually_exclusive_group(required=True)
g2.add_argument("-f", "--filename", type=str, help="file of hosts, one per line")
g2.add_argument("-s", "--singlehost", type=str, help="single host/ip to run against")

g3 = parser.add_argument_group()
g3.add_argument("-u", "--username", type=str, required=True,
                help="username to use for SSH connection")

args = parser.parse_args()
password = getpass.getpass("SSH password for {}: ".format(args.username))

if args.filename != None:
    with open(args.filename) as f:
        for line in f:
            line = line.strip()
            if hostname_resolves(line):
                if check_ssh(line, args.username, password):
                    print "{},connection successful".format(line)
                else:
                    print "{},connection failed".format(line)
            else:
                print "{},failed to resolve".format(line)
else:
    if hostname_resolves(args.singlehost):
        if check_ssh(args.singlehost, args.username, password):
            print "{},connection successful".format(args.singlehost)
        else:
            print "{},connection failed".format(args.singlehost)
    else:
        print "{},failed to resolve".format(args.singlehost)
