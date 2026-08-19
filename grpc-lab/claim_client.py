import grpc
import item_pb2
import item_pb2_grpc
from lamport_clock import LamportClock 

def run():
    clock = LamportClock()
    
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = item_pb2_grpc.ItemServiceStub(channel)
        
        # 1. Check availability
        print("========== CHECK ITEM ==========")
        req_time = clock.send_event()
        print(f"Sending Request | Lamport Clock : {req_time}")
        
        item_request = item_pb2.ItemRequest(item_id="123", lamport_clock=req_time)
        item_response = stub.CheckItemAvailability(item_request)
        
        clock.receive_event(item_response.lamport_clock)
        print(f"Received Response | Lamport Clock : {clock.time}")
        print(f"Available: {item_response.available}\n")
        
        # 2. Submit Claim
        if item_response.available:
            print("========== SUBMIT CLAIM ==========")
            req_time = clock.send_event()
            print(f"Sending Request | Lamport Clock : {req_time}")
            
            claim_request = item_pb2.ClaimRequest(item_id="123", user_email="test@test.com", lamport_clock=req_time)
            claim_response = stub.SubmitClaim(claim_request)
            
            clock.receive_event(claim_response.lamport_clock)
            print(f"Received Response | Lamport Clock : {clock.time}")
            print(f"Success: {claim_response.success}")

if __name__ == '__main__':
    run()