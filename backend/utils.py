import time, subprocess, sys

def measure_runtime(filepath: str, runs: int = 3) -> float:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        proc = subprocess.run([sys.executable, filepath], capture_output=True)
        end = time.perf_counter()
        if proc.returncode != 0:
            raise RuntimeError(f"{filepath} crashed:\n{proc.stderr.decode()}")
        times.append((end - start) * 1000)
    return round(sum(times) / len(times), 3)
