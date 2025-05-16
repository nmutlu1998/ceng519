import asyncio
from nats.aio.client import Client as NATS
import os
import random
from scapy.all import Ether, IP, UDP, DNS, DNSQR
import time
import pickle
import argparse
import base64
import codecs
from detector import Detector
import time
from collections import defaultdict

# Track timestamps of malign access per domain/IP
throttle_tracker = defaultdict(list)
THROTTLE_LIMIT = 5  # max 5 malign requests
TIME_WINDOW = 60    # in seconds

ml_model = Detector()

def is_throttled(source):
    now = time.time()
    throttle_tracker[source] = [t for t in throttle_tracker[source] if now - t < TIME_WINDOW]

    if len(throttle_tracker[source]) >= THROTTLE_LIMIT:
        return True
    throttle_tracker[source].append(now)
    return False

async def run(message, chunk_size, encoding_scheme):

    nc = NATS()
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data

        packet = Ether(data)

        if packet.haslayer(DNS):
            dns_id = packet[DNS].id

            if packet[DNS].qr == 0:
                for query in packet[DNS].qd:
                    domain = query.qname.decode()

                    print(f"DNS Query ID: {dns_id}, Requested Domain: {domain}")
                    result = ml_model.predict(domain)
                    print(f"Subdomain: {subdomain} result ", result)
                    if result[0] != 0:
                        if is_throttled(domain):  # or source IP
                            print(f"Rate limit exceeded for {domain}")
                            # drop, delay, or flag request
                        else:
                            print(f"Malign request from {domain}, logged")

        if subject == "inpktsec":
            await nc.publish("outpktinsec", bytes(packet))
        else:
            await nc.publish("outpktsec", msg.data)

   
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Subscribed to inpktsec and inpktinsec topics")

    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        await nc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DNS Covert Channel Encoder")