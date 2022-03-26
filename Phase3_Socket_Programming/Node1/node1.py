import time
import socket
import json
import threading
import random

Timeout = random.uniform(.25, .35)
currentTerm = 0
votedFor = ""
Log = []
Heartbeat = .1
isLeader = True
name = "Node1"
nodes = ["Node2", "Node3"]
currentLeader = ""
state = "follower"

def heartbeat(skt):
    append_rpc = {"leaderId": f"Node1", "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        if isLeader:
            time.sleep(Heartbeat)
            for node in nodes:
                skt.sendto(json.dumps(append_rpc).encode(), (node, 5555))
                print("sent to " + node)

if __name__ == "__main__":

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()
    # Bind the node to sender ip and port
    UDP_Socket.bind((name, 5555))

    print("All messages were sent")
    print("Ending Node 1")
