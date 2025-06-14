import asyncio
from nats.aio.client import Client as NATS
import os
from scapy.all import Ether, IP, UDP, DNS, DNSQR
import argparse
from models.detector import Detector
import time
from collections import defaultdict

ml_model = Detector()

throttle_tracker = defaultdict(list)
THROTTLE_LIMIT = 5
TIME_WINDOW = 60

total_encoded_received = defaultdict(int)
total_encoded_allowed = defaultdict(int)
start_time = time.time()

def is_throttled(source, limit, window, is_limitless = False):
    now = time.time()
    throttle_tracker[source] = [t for t in throttle_tracker[source] if now - t < window]

    if not is_limitless:
        if len(throttle_tracker[source]) >= limit:
            return True
    throttle_tracker[source].append(now)
    return False

def calculate_capacity(chunk_size):
    now = time.time()
    duration = now - start_time
    if duration == 0:
        return 0.0

    total_bits = sum(total_encoded_allowed[src] * chunk_size * 8 for src in total_encoded_allowed)
    return total_bits / duration

async def run(throttle_limit, time_window, chunk_size, is_limitless=False):

    nc = NATS()
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data

        packet = Ether(data)

        if packet.haslayer(DNS) and packet[DNS].qr == 0:
            for query in packet[DNS].qd:
                domain = query.qname.decode()
                src_ip = packet[IP].src if packet.haslayer(IP) else "unknown"

                result = ml_model.predict(domain)

                if result != 0:
                    total_encoded_received[src_ip] += 1

                    if is_throttled(src_ip, throttle_limit, time_window, is_limitless):
                        print(f"[THROTTLED] {src_ip} - {domain}")
                        return
                    else:
                        total_encoded_allowed[src_ip] += 1
                        print(f"[ALLOWED] {src_ip} - {domain} (encoded)")

        if subject == "inpktsec":
            await nc.publish("outpktinsec", bytes(packet))
        else:
            await nc.publish("outpktsec", msg.data)

    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Subscribed to inpktsec and inpktinsec topics")

    try:
        while True:
            await asyncio.sleep(10)
            capacity = calculate_capacity(chunk_size)
            print(f"[Capacity Report] Covert Channel Capacity: {capacity:.2f} bits/sec")
    except Exception as e:
        print(f"Error occurred: {e}")
        await nc.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DNS Covert Channel Encoder")
    parser.add_argument('--throttle-limit', type=int, default=5, help='Max requests per source in time window')
    parser.add_argument('--time-window', type=int, default=60, help='Time window for throttling in seconds')
    parser.add_argument('--chunk-size', type=int, default=8, help='Size of each data chunk of dns sender (in characters, added for metrics)')

    args = parser.parse_args()

    THROTTLE_LIMIT = args.throttle_limit
    TIME_WINDOW = args.time_window

    is_limitless = THROTTLE_LIMIT == -1
    asyncio.run(run(THROTTLE_LIMIT, TIME_WINDOW, args.chunk_size, is_limitless))