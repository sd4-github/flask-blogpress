# =============================================================================
# python_scripts/03_threading_advanced.py  --  LEVEL: ADVANCED (Flask-flavoured)
# =============================================================================
# Purpose: concurrency in the WSGI/threading model Flask uses.
#   * Flask (dev) serves one request per THREAD. So understanding threads,
#     locks, and thread-safety is key — unlike FastAPI's async event loop.
#   * In production you run gunicorn with multiple workers (processes).
#   * Topics: threading.Thread, locks, thread pools, GIL, daemon threads,
#     race conditions (classic interview topic).
#
# NOTE: For CPU-bound work, threads are limited by the GIL; use processes or
# offload to Celery (which we do in app/tasks.py). For I/O threads are fine.
# Run:  .venv/bin/python python_scripts/03_threading_advanced.py

import threading
import time
from concurrent.futures import ThreadPoolExecutor

COUNTER = 0                      # a shared variable all threads mutate (danger zone)


def counter_thread(num_increments: int, lock: threading.Lock) -> None:
    """Increment a shared counter. With a lock this is safe; without it,
       thread schedulers interleave `read -> add -> write` causing lost updates
       (a classic interview example of a race condition)."""
    global COUNTER
    for _ in range(num_increments):
        with lock:
            COUNTER += 1


def demonstrate_race():
    global COUNTER
    COUNTER = 0
    lock = threading.Lock()
    threads = [threading.Thread(target=counter_thread, args=(1000, lock)) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()                 # wait for all threads to finish
    print(f"expected {10*1000} with lock -> got {COUNTER}")


def io_like_work(item: int) -> int:
    """Simulate an I/O-bound task (e.g. an external HTTP call inside a Flask
       endpoint). Concurrency here is a real win even with the GIL, because
       the GIL is released during I/O waits."""
    time.sleep(0.1)              # blocking I/O (releases GIL)
    return item * 2


def demonstrate_pool():
    """ThreadPoolExecutor runs many I/O tasks concurrently — this is exactly
       what a WSGI server does per incoming request (if async, use a pool)."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(io_like_work, range(12)))
    print(f"12 I/O tasks via pool in {time.perf_counter()-start:.2f}s -> {results}")


def daemon_example():
    """A daemon thread dies when the main program exits (good for background
       keep-alives that must not block shutdown). Similar to how Flask's dev
       server or a fire-and-forget background task might behave."""
    stop = threading.Event()

    def work():
        while not stop.is_set():
            time.sleep(0.2)

    t = threading.Thread(target=work, daemon=True)
    t.start()
    print("daemon started")
    time.sleep(0.3)
    stop.set()                   # signal it to stop


if __name__ == "__main__":
    demonstrate_race()
    demonstrate_pool()
    daemon_example()
    print("\nThreads released the GIL for I/O; for CPU-bound work, prefer "
          "multiprocessing/processes or Celery (see app/tasks.py).")
