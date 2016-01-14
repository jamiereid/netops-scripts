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

def disable_paging(conn):
    '''Disable paging on a Cisco router'''

    conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = conn.recv(1000)

    return output

def ssh_apply_config(host, config, username, password, port=22):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, password=password)
    except Exception as e:
        print e
    else:
        conn = client.invoke_shell()
        output = conn.recv(1000)
        time.sleep(1)
        disable_paging(conn)

        conn.send('enable\n')
        time.sleep(1)
        output = conn.recv(10000)
        conn.send('conf t\n')
        time.sleep(1)
        output = conn.recv(10000)

        with open(config) as f:
            for line in f:
                conn.send(line.strip() + '\n')
                time.sleep(1)
                output = conn.recv(10000)

        print "{},config applied".format(host)

    client.close()

parser = argparse.ArgumentParser()

#g1 = parser.add_mutually_exclusive_group()
#g1.add_argument("-v", "--verbose", action="count", default=0,
#                help="increase output verbosity")
#g1.add_argument("-q", "--quiet", action="store_true",
#                help="supress all output")

parser.add_argument("-c", "--config", type=str, required=True, help="file containing config to apply")

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
                print "{},applying config".format(line)
                ssh_apply_config(line, args.config, args.username, password)
            else:
                print "{},failed to resolve".format(line)
else:
    if hostname_resolves(args.singlehost):
        print "{},applying config".format(args.singlehost)
        ssh_apply_config(args.singlehost, args.config, args.username, password)
    else:
        print "{},failed to resolve".format(args.singlehost)
