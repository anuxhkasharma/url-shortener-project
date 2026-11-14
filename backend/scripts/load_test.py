import statistics
import time

import redis
import requests

BASE = "http://127.0.0.1:8000"
CODE = "y2fy78"
N = 200

r = redis.Redis.from_url("redis://localhost:6379/0")
session = requests.Session()  # connection reuse, fair measurement


def timed_get():
    start = time.perf_counter()
    session.get(f"{BASE}/{CODE}", allow_redirects=False)
    return (time.perf_counter() - start) * 1000


def summarize(name, times):
    times = sorted(times)
    print(f"{name}: avg={statistics.mean(times):.2f} ms, "
          f"median={statistics.median(times):.2f} ms, "
          f"p95={times[int(len(times) * 0.95) - 1]:.2f} ms")



for _ in range(5):
    timed_get()


miss_times = []
for _ in range(N):
    r.delete(f"url:{CODE}")
    miss_times.append(timed_get())


timed_get()
hit_times = [timed_get() for _ in range(N)]

summarize("Without cache (PostgreSQL)", miss_times)
summarize("With cache (Redis)       ", hit_times)