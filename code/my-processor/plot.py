import pickle
import numpy as np
import matplotlib.pyplot as plt

with open("rtts.pkl", "rb") as f:
    rtt_values = pickle.load(f)

with open("delays.pkl", "rb") as f:
    delay_values = pickle.load(f)

mean_random_delay = np.mean(delay_values) if delay_values else 0
avg_rtt = np.mean(rtt_values) if rtt_values else 0

plt.figure(figsize=(8, 5))
plt.scatter(delay_values, rtt_values, color='blue', alpha=0.6, label="RTT vs Delay")


plt.xlabel("Random Delay (ms)")
plt.ylabel("RTT (ms)")
plt.title("Mean Random Delay vs Average RTT")
plt.legend()
plt.grid(True)

plt.show()

