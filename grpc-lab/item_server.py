import grpc
from concurrent import futures
import time
import item_pb2
import item_pb2_grpc
from lamport_clock import LamportClock 

class ItemServiceServicer(item_pb2_grpc.ItemServiceServicer):
    def __init__(self):
        self.clock = LamportClock()

    def CheckItemAvailability(self, request, context):
        # Update clock on receive
        self.clock.receive_event(request.lamport_clock)
        print(f"Received Check Request. Lamport Clock: {self.clock.time}")
        
        # Increment clock on send
        send_time = self.clock.send_event()
        if request.item_id == "123":
            return item_pb2.ItemResponse(available=True, message="Item is available.", lamport_clock=send_time)
        return item_pb2.ItemResponse(available=False, message="Item not found.", lamport_clock=send_time)

    def SubmitClaim(self, request, context):
        self.clock.receive_event(request.lamport_clock)
        print(f"Received Claim Request. Lamport Clock: {self.clock.time}")
        
        send_time = self.clock.send_event()
        return item_pb2.ClaimResponse(success=True, message="Claim processed.", lamport_clock=send_time)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    item_pb2_grpc.add_ItemServiceServicer_to_server(ItemServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Item Service Started on Port 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()