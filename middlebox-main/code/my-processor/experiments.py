import subprocess
import itertools
import time

chunk_sizes = [4, 8, 16]
encoding_schemes = ['base64', 'hex', 'rot13']
message = "Contrary to popular belief, Lorem Ipsum is not simply random text. "
runs_per_config = 10
def run_experiment(chunk_size, encoding, run_id):
    print(f"\n[Experiment] Chunk Size: {chunk_size}, Encoding: {encoding}, Run: {run_id}")
    
    cmd = [
        "python", "main.py",
        "--message", message,
        "--chunk-size", str(chunk_size),
        "--encoding", encoding
    ]
    try:
        subprocess.run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        print(f"Timeout for Chunk Size {chunk_size}, Encoding {encoding}")

if __name__ == "__main__":
    for chunk_size, encoding in itertools.product(chunk_sizes, encoding_schemes):
        for run_id in range(runs_per_config):
            run_experiment(chunk_size, encoding, run_id)
            time.sleep(5)
