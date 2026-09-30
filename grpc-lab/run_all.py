"""
Launches node.py 1, node.py 2, node.py 3 at the same instant as subprocesses,
and streams all their output into this one terminal with [Node-N] prefixes.

Run with:  python run_all.py
(venv must already be active in this terminal)
"""

import subprocess
import sys
import threading

NUM_NODES = 3


def stream(proc, node_id):
    for line in proc.stdout:
        print(f"[Node-{node_id}] {line}", end="")


def main():
    procs = []
    # Start all three at once - back-to-back Popen calls, no sleeps between them
    for i in range(1, NUM_NODES + 1):
        proc = subprocess.Popen(
            [sys.executable, "node.py", str(i)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(proc)

    threads = []
    for i, proc in enumerate(procs, start=1):
        t = threading.Thread(target=stream, args=(proc, i), daemon=True)
        t.start()
        threads.append(t)

    for proc in procs:
        proc.wait()
    for t in threads:
        t.join(timeout=1)

    print("\nAll nodes finished.")


if __name__ == "__main__":
    main()