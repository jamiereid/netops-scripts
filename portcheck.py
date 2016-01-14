#!/usr/bin/python

import socket
import sys
import argparse

def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0

def check_ports(ports, host, timeout=60):
    if hostname_resolves(host):
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
            except Exception,e:
                print "{} closed for host {}".format(port, host)
            else:
                print "{} open for host {}".format(port, host)
            sock.close()
    else:
        print "Unable to resolve {}".format(host)

parser = argparse.ArgumentParser()

#g1 = parser.add_mutually_exclusive_group()
#g1.add_argument("-v", "--verbose", action="count", default=0,
#                help="increase output verbosity")
#g1.add_argument("-q", "--quiet", action="store_true",
#                help="supress all output")

parser.add_argument("-p", "--port", type=int, required=True, action="append", metavar="PORT", dest="ports",
                    help="the port to check (can be specified multiple times)")

g2 = parser.add_mutually_exclusive_group(required=True)
g2.add_argument("-f", "--filename", type=str, help="a file to parse, one ip/hostname per line")
g2.add_argument("-s", "--singlehost", type=str, help="a single host/ip to run against")

args = parser.parse_args()

if args.filename != None:
    with open(args.filename) as f:
        for line in f:
            line = line.strip()
            check_ports(args.ports, line, 2)
else:
    check_ports(args.ports, args.singlehost, 2)
