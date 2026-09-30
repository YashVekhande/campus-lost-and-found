import sys
import time
import random
from concurrent import futures
 
import grpc
import item_pb2
import item_pb2_grpc
 
 
class WorkerServicer(item_pb2_grpc.WorkerServiceServicer):
    def __init__(self, name):
        self.name = name
 
    def HandleRequest(self, request, context):
        work_time = random.uniform(0.5, 2.5)  # simulate variable processing time
        print(f"[{self.name}] Handling request {request.request_id} (will take {work_time:.1f}s)")
        time.sleep(work_time)
        print(f"[{self.name}] Finished request {request.request_id}")
        return item_pb2.WorkReply(
            request_id=request.request_id,
            handled_by=self.name,
            status="done",
        )

 
def serve(port):
    name = f"Worker-{port}"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    item_pb2_grpc.add_WorkerServiceServicer_to_server(WorkerServicer(name), server)
    server.add_insecure_port(f"localhost:{port}")
    server.start()
    print(f"{name} listening on localhost:{port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
 
 
if __name__ == "__main__":
    serve(int(sys.argv[1]))
