import time
import subprocess
import sys
from typing import Optional

def measure_runtime(filepath: str, runs: int = 3, timeout_per_run: Optional[int] = 10) -> float:
    """
    Measure average runtime in milliseconds for executing the Python file.
    Raises RuntimeError on non-zero exit or timeout.
    """
    times = []
    for i in range(runs):
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                [sys.executable, filepath],
                capture_output=True,
                timeout=timeout_per_run
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"{os.path.basename(filepath)} timed out after {timeout_per_run} seconds (run {i+1}).")
        end = time.perf_counter()

        if proc.returncode != 0:
            stderr = proc.stderr.decode(errors="ignore")
            raise RuntimeError(f"{os.path.basename(filepath)} crashed (return code {proc.returncode}):\n{stderr}")

        times.append((end - start) * 1000.0)  # ms

    avg = sum(times) / len(times)
    return round(avg, 3)
