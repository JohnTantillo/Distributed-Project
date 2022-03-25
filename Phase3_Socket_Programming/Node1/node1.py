import time
import socket
import json
import threading


# def create_msg(counter):
#     msg = {"msg": f"Hi, I am Node", "counter":counter}
#     msg_bytes = json.dumps(msg).encode()
#     return msg_bytes

def heartbeat(skt):
    target = "Node2"
    append_rpc = {"leaderId": f"Node1", "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        time.sleep(1)
        skt.sendto(json.dumps(append_rpc).encode(), (target, 5555))
        print("sent")

if __name__ == "__main__":

    print("Starting Node 1")
    time.sleep(5)

    sender = "Node1"
    target = "Node2"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()
    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    # Sending 5 messages to Node 2
    # for i in range(5):
    #     node1_msg_bytes = create_msg(i)
    #     UDP_Socket.sendto(node1_msg_bytes, (target, 5555))
    #     time.sleep(1)

    print("All messages were sent")
    print("Ending Node 1")
