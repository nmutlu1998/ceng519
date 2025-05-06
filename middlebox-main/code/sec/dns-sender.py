import subprocess
import argparse
import time
from scapy.all import Ether, IP, UDP, DNS, DNSQR, sendp

def send_dns_query(base_domain, id):
    dns_query = Ether()/IP(dst='insec')/UDP(dport=53)/DNS(id=id, rd=1, qd=DNSQR(qname=base_domain))
    sendp(dns_query)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=100, help="Interval between packets (ms)")
    parser.add_argument("--count", type=int, default=10, help="Number of packets to send")
    parser.add_argument("--base-domain", type=str, default="covert.local", help="Base domain for DNS queries")

    args = parser.parse_args()

    print(f"Sending {args.count} DNS packets to domain *.{args.base_domain} every {args.interval}ms")

    i = 0
    while True:
        send_dns_query(args.base_domain, i)
        time.sleep(args.interval / 1000.0)
        i += 1