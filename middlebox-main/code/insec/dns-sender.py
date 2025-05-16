import subprocess
import argparse
import time
from scapy.all import Ether, IP, UDP, DNS, DNSQR, sendp
import asyncio
from nats.aio.client import Client as NATS
import os
import random
import base64
import codecs

def encode_message(msg, encoding_scheme):
    if encoding_scheme == 'base64':
        return base64.urlsafe_b64encode(msg.encode()).decode()
    elif encoding_scheme == 'hex':
        return msg.encode().hex()
    elif encoding_scheme == 'rot13':
        return codecs.encode(msg, 'rot_13')

def send_dns_query(domain, id):
    dns_query = Ether()/IP(dst='sec')/UDP(dport=53)/DNS(id=id, rd=1, qd=DNSQR(qname=domain))
    sendp(dns_query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=100, help="Interval between packets (ms)")
    parser.add_argument("--count", type=int, default=10, help="Number of packets to send")
    parser.add_argument("--base-domain", type=str, default="covert.local", help="Base domain for DNS queries")
    parser.add_argument('--message', type=str, required=True, help='The secret message to send')
    parser.add_argument('--chunk-size', type=int, default=8, help='Payload size per DNS query (in bytes)')
    parser.add_argument('--encoding', type=str, choices=['base64', 'hex', 'rot13'], default='base64', help='Encoding scheme for the message')

    args = parser.parse_args()
    print(f"Sending {args.count} DNS packets to domain *.{args.base_domain} every {args.interval}ms")

    send_times = {}
    rtts = []

    message = args.message
    chunk_size = args.chunk_size
    encoding_scheme = args.encoding

    chunks = [encode_message(message[i:i+chunk_size], encoding_scheme) for i in range(0, len(message), chunk_size)]
    i = 0
    while True:
        if (i >= len(chunks)):
            break
        send_dns_query(chunks[i] + "." + args.base_domain, i)
        time.sleep(args.interval / 1000.0)
        i += 1