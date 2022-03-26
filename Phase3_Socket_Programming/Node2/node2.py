import socket
import time
import threading
import json
import traceback
import random

Timeout = random.uniform(.25, .35)
currentTerm = 0
votedFor = ""
Log = []
Heartbeat = .1
isLeader = False
name = "Node2"
nodes = ["Node1", "Node2"]
currentLeader = ""
state = "follower"


# Listener
def listener(skt):
    print(f"Starting Listener ")
    start_time = 0
    while True:
        stop_time = time.perf_counter()
        if start_time != 0 and stop_time - start_time > Timeout:
            print("TIMEOUT!!!")
        try:
            msg, addr = skt.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")
        # Decoding the Message received from Node 1
        decoded_msg = json.loads(msg.decode('utf-8'))
        print(f"Message Received : {decoded_msg} From : {addr}")
        if decoded_msg['prevLogIndex'] == -1:
            start_time = time.perf_counter()
        stop_time = time.perf_counter()
        print(str(stop_time-start_time))

    print("Exiting Listener Function")

def heartbeat(skt):
    append_rpc = {"leaderId": f"Node2", "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        if isLeader:
            time.sleep(Heartbeat)
            for node in nodes:
                skt.sendto(json.dumps(append_rpc).encode(), (node, 5555))
                print("sent to " + node)

if __name__ == "__main__":
    print(f"Starting Node 2")

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((name, 5555))
    UDP_Socket.settimeout(Timeout)
    #Starting thread 1
    threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2

    print("Started both functions, Sleeping on the main thread for 10 seconds now")
    time.sleep(10)
    print(f"Completed Node Main Thread Node 2")
