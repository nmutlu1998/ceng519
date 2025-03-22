import asyncio
from nats.aio.client import Client as NATS
import os, random
from scapy.all import Ether, IP, ICMP
import time
import pickle

async def run():
    delays = []
    send_times = {}
    rtts = []

    nc = NATS()
    
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data #.decode()
        #print(f"Received a message on '{subject}': {data}")
        packet = Ether(data)
        print(packet.show())

        # Publish the received message to outpktsec and outpktinsec
        delay = random.expovariate(1 / 5e-6)
        await asyncio.sleep(delay)

        if packet.haslayer(IP) and packet.haslayer(ICMP):
            icmp = packet[ICMP]
            if icmp.type == 8:
                 send_times[icmp.id] = time.time()
                 delays.append(delay)
            elif icmp.type == 0:
                if icmp.id in send_times:
                    rtt = time.time() - send_times[icmp.id]
                    rtts.append(rtt)
        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)
   
    # Subscribe to inpktsec and inpktinsec topics
    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)

    print("Subscribed to inpktsec and inpktinsec topics")

    try:
        while True:
            await asyncio.sleep(1)
    except:
        with open("rtts.pkl", "wb") as f:
            pickle.dump(rtts, f)

        with open("delays.pkl", "wb") as f:
            pickle.dump(delays, f)
        print("Disconnecting...")
        await nc.close()

if __name__ == '__main__':
    asyncio.run(run())
