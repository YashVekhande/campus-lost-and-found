"""
DC Lab - Experiment 5
Central Lock Manager - deadlock simulation and (optional) detection.

Two shared records: "item" and "claim".
- Claim submission locks item -> then claim
- Claim verification locks claim -> then item

Run without an argument for simulation mode (a real deadlock will just hang):
    python lock_manager.py
Run with "detect" for detection mode (cycles are caught and the newer
requester is aborted instead of hanging):
    python lock_manager.py detect
"""

import sys
import threading
import time
from concurrent import futures

import grpc
import item_pb2
import item_pb2_grpc

DETECT = (len(sys.argv) > 1 and sys.argv[1] == "detect")


class LockManager(item_pb2_grpc.LockServiceServicer):
    def __init__(self):
        self.mutex = threading.Lock()
        self.locks = {"item": None, "claim": None}
        self.wait_for = {}  # holder_id -> resource_id they're waiting on
        self.conditions = {"item": threading.Condition(), "claim": threading.Condition()}

    def _would_cycle(self, holder, resource):
        """Walk the wait-for chain starting at the current owner of `resource`.
        If it eventually leads back to `holder`, granting this wait creates a cycle."""
        visited = set()
        current_resource = resource
        while True:
            owner = self.locks.get(current_resource)
            if owner is None or owner == holder:
                return owner == holder
            if owner in visited:
                return False
            visited.add(owner)
            current_resource = self.wait_for.get(owner)
            if current_resource is None:
                return False

    def AcquireLock(self, request, context):
        resource, holder, ts = request.resource_id, request.holder_id, request.timestamp
        cond = self.conditions[resource]

        with cond:
            with self.mutex:
                owner = self.locks.get(resource)
                if owner is None:
                    self.locks[resource] = holder
                    self.wait_for.pop(holder, None)
                    return item_pb2.LockReply(granted=True, message="granted")

                if DETECT and self._would_cycle(holder, resource):
                    print(
                        f"[LockManager] DEADLOCK DETECTED: Node-{holder} -> '{resource}' "
                        f"(held by Node-{owner}) would close a cycle. Aborting Node-{holder}."
                    )
                    return item_pb2.LockReply(granted=False, message="deadlock-abort")

                self.wait_for[holder] = resource
                print(f"[LockManager] Node-{holder} WAITING for '{resource}' (held by Node-{owner})")

            while True:
                with self.mutex:
                    owner = self.locks.get(resource)
                    if owner is None:
                        self.locks[resource] = holder
                        self.wait_for.pop(holder, None)
                        return item_pb2.LockReply(granted=True, message="granted-after-wait")
                cond.wait(timeout=1)

    def ReleaseLock(self, request, context):
        resource, holder = request.resource_id, request.holder_id
        cond = self.conditions[resource]

        with cond:
            with self.mutex:
                if self.locks.get(resource) == holder:
                    self.locks[resource] = None
                cond.notify_all()
                return item_pb2.LockReply(granted=True, message="released")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    item_pb2_grpc.add_LockServiceServicer_to_server(LockManager(), server)
    server.add_insecure_port("localhost:60100")
    server.start()
    print(f"LockManager started on localhost:60100 (deadlock detection = {DETECT})")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()