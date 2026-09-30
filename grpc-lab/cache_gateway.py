"""
DC Lab - Experiment 8
Cache-aside gateway sitting in front of the existing ItemService (Exp 2/3's
item_server.py, reused with zero code changes). Reads go through Redis
first; on a miss, or if Redis itself is unavailable, the gateway falls
through to the real backend. If the backend is unavailable, it falls back
to a never-expiring "stale" backup entry instead of returning an error.

Usage:
    python cache_gateway.py <item_id>
    e.g. python cache_gateway.py 123
"""

import json
import sys

import grpc
import redis

import item_pb2
import item_pb2_grpc
from lamport_clock import LamportClock

REDIS_HOST = "localhost"
REDIS_PORT = 6379
CACHE_TTL_SECONDS = 10  # short TTL so hits/misses are easy to observe
BACKEND_SERVICE_ADDR = "localhost:50051"
STALE_KEY_PREFIX = "stale:item:"  # kept indefinitely as a fallback, never expires
FRESH_KEY_PREFIX = "fresh:item:"  # normal cache entry, expires after CACHE_TTL_SECONDS


def get_redis():
    """Fresh connection per call, with a short timeout, so we can detect
    Redis being down quickly instead of hanging."""
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=1, socket_timeout=1
    )


def fetch_from_backend(item_id):
    """Direct call to the real backend service - item_server.py from Exp 2/3,
    unchanged. Carries a Lamport timestamp on the request, same as
    claim_client.py does, and updates the local clock on the reply."""
    with grpc.insecure_channel(BACKEND_SERVICE_ADDR) as channel:
        stub = item_pb2_grpc.ItemServiceStub(channel)
        clock = LamportClock()
        req_ts = clock.send_event()
        response = stub.CheckItemAvailability(
            item_pb2.ItemRequest(item_id=item_id, lamport_clock=req_ts), timeout=2
        )
        clock.receive_event(response.lamport_clock)
        return {"item_id": item_id, "available": response.available, "message": response.message}


def get_item(item_id):
    fresh_key = f"{FRESH_KEY_PREFIX}{item_id}"
    stale_key = f"{STALE_KEY_PREFIX}{item_id}"

    # --- Try the cache first ---
    try:
        r = get_redis()
        cached = r.get(fresh_key)
        if cached:
            print(f"[Gateway] CACHE HIT for item {item_id}")
            return json.loads(cached), "cache-hit"
        print(f"[Gateway] CACHE MISS for item {item_id} -- querying backend")
    except redis.exceptions.RedisError as e:
        print(f"[Gateway] REDIS UNAVAILABLE ({e}) -- falling back to backend directly")
        r = None

    # --- Cache miss, or Redis itself is down: go to the real backend ---
    try:
        data = fetch_from_backend(item_id)
        print(f"[Gateway] Fetched item {item_id} from BACKEND")
        if r is not None:
            try:
                r.set(fresh_key, json.dumps(data), ex=CACHE_TTL_SECONDS)
                r.set(stale_key, json.dumps(data))  # no expiry - fault-tolerance backup
            except redis.exceptions.RedisError:
                print("[Gateway] Redis write failed, continuing without caching this result")
        return data, "backend"

    except grpc.RpcError as e:
        # --- Backend unreachable: fall back to a stale cached copy if we have one ---
        print(f"[Gateway] BACKEND UNAVAILABLE ({e.code()}) -- checking for stale cache")
        if r is not None:
            try:
                stale = r.get(stale_key)
                if stale:
                    print(f"[Gateway] Serving STALE cached copy for item {item_id}")
                    return json.loads(stale), "stale-fallback"
            except redis.exceptions.RedisError:
                pass
        raise RuntimeError(f"Item {item_id} unavailable: both backend and cache failed")


if __name__ == "__main__":
    item_id = sys.argv[1] if len(sys.argv) > 1 else "123"
    data, source = get_item(item_id)
    print(f"\nResult (source={source}): {data}")