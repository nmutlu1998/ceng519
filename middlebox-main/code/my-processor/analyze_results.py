import os
import numpy as np
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
chunk_sizes = [2, 4, 8]
encoding_schemes = ['base64', 'hex']

message_length_bytes = len("Contrary to popular belief, Lorem Ipsum is not simply random text. ")
bits_per_byte = 8

def load_rtts(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        return [float(line.strip()) for line in lines]

def confidence_interval(data, confidence=0.95):
    if len(data) == 0:
        return (0, 0)
    mean = np.mean(data)
    sem = stats.sem(data)
    margin = sem * stats.t.ppf((1 + confidence) / 2., len(data) - 1)
    return (mean, margin)

def calculate_capacity(chunk_size, encoding, rtts):
    total_bits = message_length_bytes * bits_per_byte
    total_time = sum(rtts)  # Total RTT sum
    throughput_bps = total_bits / total_time
    return throughput_bps

results = []

for chunk_size in chunk_sizes:
    for encoding in encoding_schemes:
        filename = f"{chunk_size}_{encoding}_rtts.txt"

        rtts = load_rtts(filename)

        avg_rtt, rtt_margin = confidence_interval(rtts)
        capacity = calculate_capacity(chunk_size, encoding, rtts)

        results.append((chunk_size, encoding, avg_rtt, rtt_margin, capacity))

print("\n=== Experiment Results ===")

for chunk_size, encoding, avg_rtt, rtt_margin, capacity in results:
    print("Chunk Size:" + str(chunk_size) + " Encoding Scheme:" + encoding + " Avg RTT: " + str(avg_rtt) + " 95% CI Margin: " + str(rtt_margin) +  " Capacity: " + str(capacity))

plt.figure(figsize=(10, 6))
for encoding in encoding_schemes:
    enc_caps = [cap for (chunk, enc, avg, margin, cap) in results if enc == encoding]
    enc_chunks = [chunk for (chunk, enc, avg, margin, cap) in results if enc == encoding]
    plt.plot(enc_chunks, enc_caps, marker='o', label=encoding)

plt.title("Capacity vs Chunk Size for Different Encodings")
plt.xlabel("Chunk Size (bytes)")
plt.ylabel("Capacity (bits per second)")
plt.legend()
plt.grid()
plt.savefig('capacity_plot.png')


plt.figure(figsize=(10, 6))

for encoding in encoding_schemes:
    enc_caps = [cap for (chunk, enc, avg, margin, cap) in results if enc == encoding]
    enc_chunks = [chunk for (chunk, enc, avg, margin, cap) in results if enc == encoding]

    if encoding == 'base64':
        plt.plot(enc_chunks, enc_caps, marker='o', label=f'Base64 Encoding', linestyle='-', color='blue')
    elif encoding == 'hex':
        plt.plot(enc_chunks, enc_caps, marker='x', label=f'Hex Encoding', linestyle='--', color='red')

plt.title("Capacity vs Chunk Size for Different Encodings")
plt.xlabel("Chunk Size (bytes)")
plt.ylabel("Capacity (bits per second)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('capacity_encoding.png')


