"""
DC Lab - Experiment 7
Client that deliberately creates a conflict: two "staff counters" hit two
different replicas with a status update for the SAME item at nearly the
same time, then checks that all replicas eventually converge.
"""

import time
import threading

import grpc
import item_pb2
import item_pb2_grpc

REPLICAS = {"A": "localhost:60301", "B": "localhost:60302", "C": "localhost:60303"}


def save(replica_name, key, content):
    with grpc.insecure_channel(REPLICAS[replica_name]) as channel:
        stub = item_pb2_grpc.ReplicaServiceStub(channel)
        ack = stub.SaveValue(
            item_pb2.ValueUpdate(key=key, content=content, lamport_timestamp=0, origin_replica="")
        )
        print(
            f"[Client] Saved on Replica-{replica_name}: \"{content}\" "
            f"-> accepted={ack.accepted}, replica_ts={ack.lamport_timestamp}"
        )


def read(replica_name, key):
    with grpc.insecure_channel(REPLICAS[replica_name]) as channel:
        stub = item_pb2_grpc.ReplicaServiceStub(channel)
        state = stub.GetValue(item_pb2.ValueQuery(key=key))
        return state.content, state.lamport_timestamp, state.origin_replica


def main():
    key = "item-42-status"

    print("=== Simulating two staff counters updating the same item's status concurrently ===\n")
    t1 = threading.Thread(target=save, args=("A", key, "Marked CLAIMED by Counter-1"))
    t2 = threading.Thread(target=save, args=("C", key, "Marked VERIFIED-FOUND by Counter-2"))
    t1.start()
    time.sleep(0.05)  # near-simultaneous, not identical - creates a real race
    t2.start()
    t1.join()
    t2.join()

    print("\n=== Immediately after writes (replicas may still be mid-gossip) ===")
    for name in REPLICAS:
        content, ts, origin = read(name, key)
        print(f"Replica-{name}: \"{content}\" (ts={ts}, origin={origin})")

    print("\nWaiting 2s for gossip to finish propagating...\n")
    time.sleep(2)

    print("=== After convergence window ===")
    results = {}
    for name in REPLICAS:
        content, ts, origin = read(name, key)
        results[name] = content
        print(f"Replica-{name}: \"{content}\"")

    if len(set(results.values())) == 1:
        print(f"\n*** CONVERGED: all replicas agree on: \"{list(results.values())[0]}\" ***")
    else:
        print(f"\n*** NOT YET CONVERGED: {set(results.values())} ***")


if __name__ == "__main__":
    main()