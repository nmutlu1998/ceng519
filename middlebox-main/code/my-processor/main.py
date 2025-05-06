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

def encode_message(msg, encoding_scheme):
    if encoding_scheme == 'base64':
        return base64.urlsafe_b64encode(msg.encode()).decode()
    elif encoding_scheme == 'hex':
        return msg.encode().hex()
    elif encoding_scheme == 'rot13':
        return codecs.encode(msg, 'rot_13')
async def run(message, chunk_size, encoding_scheme):
    send_times = {}
    rtts = []

    nc = NATS()
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    chunks = [encode_message(message[i:i+chunk_size], encoding_scheme) for i in range(0, len(message), chunk_size)]
    print(f"Total {len(chunks)} chunks created, each chunk size up to {chunk_size} bytes.")

    chunk_index = 0

    async def message_handler(msg):
        with open(f"{chunk_size}_{encoding_scheme}_rtts.txt", "a") as f:
            nonlocal chunk_index
            subject = msg.subject
            data = msg.data

            packet = Ether(data)

            now = time.time()

            if packet.haslayer(DNS):
                dns_id = packet[DNS].id

                if packet[DNS].qr == 0 and chunk_index < len(chunks):
                    # Outgoing query
                    secret = chunks[chunk_index]
                    qname = packet[DNSQR].qname.decode()

                    new_qname = f"{secret}.{qname}"
                    packet[DNSQR].qname = new_qname.encode()

                    # Reset checksums and lengths
                    del packet[IP].len
                    del packet[IP].chksum
                    if packet.haslayer(UDP):
                        del packet[UDP].len
                        del packet[UDP].chksum

                    send_times[dns_id] = now
                    print(f"[Chunk {chunk_index}] Payload Size: {len(secret)} bytes")
                    chunk_index += 1

                elif packet[DNS].qr == 1:
                    if dns_id in send_times:
                        sent_time = send_times.pop(dns_id)
                        rtt = now - sent_time
                        rtts.append(rtt)
                        print(rtt)
                        print(rtt, file=f)
                        print(f"[Response] RTT for DNS ID {dns_id}: {rtt:.6f} seconds")

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
    parser.add_argument('--message', type=str, required=True, help='The secret message to send')
    parser.add_argument('--chunk-size', type=int, default=8, help='Payload size per DNS query (in bytes)')
    parser.add_argument('--encoding', type=str, choices=['base64', 'hex', 'rot13'], default='base64', help='Encoding scheme for the message')

    args = parser.parse_args()

    asyncio.run(run(args.message, args.chunk_size, args.encoding))
