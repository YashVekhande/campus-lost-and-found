import sys, time, random, threading
from concurrent import futures
import grpc
import item_pb2, item_pb2_grpc

ALL_NODES = {
    "A": "localhost:60401",
    "B": "localhost:60402",
    "C": "localhost:60403",
}

HEARTBEAT_INTERVAL = 0.5
ELECTION_TIMEOUT_RANGE = (1.5, 3.0)

class RaftCoordinator(item_pb2_grpc.RaftServiceServicer, item_pb2_grpc.ItemServiceServicer):
    def __init__(self, node_id):
        self.id = node_id
        self.peers = {n: addr for n, addr in ALL_NODES.items() if n != node_id}
        self.lock = threading.Lock()
        
        self.state = "FOLLOWER"
        self.current_term = 0
        self.voted_for = None
        self.leader_id = None
        self.last_heartbeat = time.time()

    def log(self, msg):
        print(f"[{self.id} term={self.current_term} {self.state}] {msg}", flush=True)

    def _reset_election_timer(self):
        self.last_heartbeat = time.time()

    def _random_timeout(self):
        return random.uniform(*ELECTION_TIMEOUT_RANGE)

    def RequestVote(self, request, context):
        with self.lock:
            if request.term > self.current_term:
                self.current_term = request.term
                self.voted_for = None
                self.state = "FOLLOWER"
            
            grant = (request.term >= self.current_term and 
                     self.voted_for in (None, request.candidate_id))
            
            if grant:
                self.voted_for = request.candidate_id
                self._reset_election_timer()
                self.log(f"Voted for {request.candidate_id} (term {request.term})")
            
            return item_pb2.VoteReply(term=self.current_term, vote_granted=grant)

    def AppendEntries(self, request, context):
        with self.lock:
            if request.term >= self.current_term:
                self.current_term = request.term
                self.state = "FOLLOWER"
                self.leader_id = request.leader_id
                self._reset_election_timer()
                return item_pb2.HeartbeatReply(term=self.current_term, success=True)
            return item_pb2.HeartbeatReply(term=self.current_term, success=False)

    def _election_watchdog(self):
        while True:
            timeout = self._random_timeout()
            time.sleep(0.1)
            elapsed = time.time() - self.last_heartbeat
            while elapsed < timeout:
                time.sleep(0.1)
                if self.state == "LEADER":
                    break
                elapsed = time.time() - self.last_heartbeat
            
            if self.state != "LEADER" and elapsed >= timeout:
                self._start_election()

    def _start_election(self):
        with self.lock:
            self.state = "CANDIDATE"
            self.current_term += 1
            self.voted_for = self.id
            term = self.current_term
            self._reset_election_timer()
            self.log("Starting election")
            
        votes = 1
        for peer_id, addr in self.peers.items():
            try:
                with grpc.insecure_channel(addr) as channel:
                    stub = item_pb2_grpc.RaftServiceStub(channel)
                    reply = stub.RequestVote(
                        item_pb2.VoteRequest(term=term, candidate_id=self.id), 
                        timeout=1
                    )
                    if reply.vote_granted:
                        votes += 1
                    elif reply.term > term:
                        with self.lock:
                            self.current_term = reply.term
                            self.state = "FOLLOWER"
                        return
            except grpc.RpcError:
                pass
        
        with self.lock:
            if self.state == "CANDIDATE" and votes > len(ALL_NODES) // 2:
                self.state = "LEADER"
                self.leader_id = self.id
                self.log(f"*** ELECTED LEADER *** ({votes}/{len(ALL_NODES)} votes)")
            else:
                self.state = "FOLLOWER"

    def _heartbeat_loop(self):
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            if self.state != "LEADER":
                continue
            for peer_id, addr in self.peers.items():
                try:
                    with grpc.insecure_channel(addr) as channel:
                        stub = item_pb2_grpc.RaftServiceStub(channel)
                        stub.AppendEntries(
                            item_pb2.HeartbeatRequest(term=self.current_term, leader_id=self.id), 
                            timeout=1
                        )
                except grpc.RpcError:
                    pass

    # --- Coordination Logic Gated Behind Leadership ---
    def SubmitClaim(self, request, context):
        with self.lock:
            if self.state != "LEADER":
                hint = self.leader_id or "unknown"
                return item_pb2.ClaimResponse(
                    success=False, 
                    message=f"not-leader, try node {hint}",
                    lamport_clock=request.lamport_clock + 1
                )
        
        self.log(f"Leader processing claim for item {request.item_id} by {request.user_email}")
        return item_pb2.ClaimResponse(
            success=True, 
            message="Claim processed successfully by LEADER",
            lamport_clock=request.lamport_clock + 1
        )

def serve(node_id):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    node = RaftCoordinator(node_id)
    
    item_pb2_grpc.add_RaftServiceServicer_to_server(node, server)
    item_pb2_grpc.add_ItemServiceServicer_to_server(node, server)
    
    port = ALL_NODES[node_id].split(":")[1]
    server.add_insecure_port(f"localhost:{port}")
    server.start()
    print(f"RaftNode-{node_id} listening on {ALL_NODES[node_id]}")
    
    threading.Thread(target=node._election_watchdog, daemon=True).start()
    threading.Thread(target=node._heartbeat_loop, daemon=True).start()
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve(sys.argv[1])