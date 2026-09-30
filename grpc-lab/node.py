"""
DC Lab - Experiment 4
Ricart-Agrawala mutual exclusion over gRPC, applied to campus-lost-and-found.

Shared resource: the "process/approve this claim" action.
Only one peer node may be inside the critical section (approving a claim)
at a time - no central coordinator, matches Exp 4's requirement.

Reuses the existing LamportClock class from lamport_clock.py (Exp 3) -
does not reimplement clock logic.

Run three copies of this file as three peer nodes:
    python node.py 1
    python node.py 2
    python node.py 3
"""

import sys
import time
import threading
from concurrent import futures

import grpc
import item_pb2
import item_pb2_grpc
from lamport_clock import LamportClock

PEERS = {1: "localhost:60051", 2: "localhost:60052", 3: "localhost:60053"}


class ClaimLockNode:
    def __init__(self, node_id):
        self.id = node_id
        self.peers = {nid: addr for nid, addr in PEERS.items() if nid != node_id}
        self.lamport = LamportClock()
        self.lamport_lock = threading.Lock()
        self.state = "RELEASED"  # RELEASED -> WANTED -> HELD
        self.request_time = None
        self.state_lock = threading.Lock()
        self.deferred = []  # threading.Events for peers we're making wait

    # --- clock helpers, delegate to the existing LamportClock ---
    def tick(self):
        with self.lamport_lock:
            return self.lamport.send_event()

    def update(self, received_ts):
        with self.lamport_lock:
            return self.lamport.receive_event(received_ts)

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        item_pb2_grpc.add_ClaimLockServiceServicer_to_server(_Servicer(self), server)
        server.add_insecure_port(PEERS[self.id])
        server.start()
        return server

    def _call_with_retry(self, addr, my_ts, max_wait=30):
        deadline = time.time() + max_wait
        while time.time() < deadline:
            try:
                with grpc.insecure_channel(addr) as channel:
                    stub = item_pb2_grpc.ClaimLockServiceStub(channel)
                    return stub.RequestAccess(
                        item_pb2.AccessRequest(node_id=self.id, timestamp=my_ts)
                    )
            except grpc.RpcError:
                time.sleep(0.5)
        raise RuntimeError(f"Could not reach {addr}")

    def request_cs(self):
        my_ts = self.tick()
        with self.state_lock:
            self.state = "WANTED"
            self.request_time = my_ts
        print(f"Node-{self.id}: WANTS claim-approval lock (ts={my_ts})")

        for peer_id, addr in self.peers.items():
            reply = self._call_with_retry(addr, my_ts)
            self.update(reply.timestamp)

        with self.state_lock:
            self.state = "HELD"
        print(f"Node-{self.id}: ENTERED critical section (approving claim)")
        time.sleep(0.5)  # simulate approving/processing a claim
        self.release_cs()
        # Keep the server alive a while longer so a slow-to-start peer can
        # still reach us even if we finished our own request early.

    def release_cs(self):
        with self.state_lock:
            self.state = "RELEASED"
            to_release, self.deferred = self.deferred, []
        print(f"Node-{self.id}: RELEASED claim-approval lock")
        for event in to_release:
            event.set()


class _Servicer(item_pb2_grpc.ClaimLockServiceServicer):
    def __init__(self, node):
        self.node = node

    def RequestAccess(self, request, context):
        node = self.node
        node.update(request.timestamp)

        with node.state_lock:
            defer = (
                node.state == "HELD"
                or (
                    node.state == "WANTED"
                    and (node.request_time, node.id) < (request.timestamp, request.node_id)
                )
            )
            event = None
            if defer:
                event = threading.Event()
                node.deferred.append(event)

        if defer:
            print(f"Node-{node.id}: DEFERS reply to Node-{request.node_id}")
            event.wait()
        else:
            print(f"Node-{node.id}: GRANTS reply to Node-{request.node_id}")

        send_ts = node.tick()
        return item_pb2.AccessReply(node_id=node.id, timestamp=send_ts)


def main():
    node = ClaimLockNode(int(sys.argv[1]))
    server = node.serve()
    time.sleep(6)  # let all 3 nodes finish starting up first
    node.request_cs()
    time.sleep(15)  # stay reachable for slower peers before shutting down
    server.stop(0)


if __name__ == "__main__":
    main()