import socket
import time
import threading
import json
import traceback
import random
import os

# Global information that will be stored in a volume
Timeout = random.uniform(.25, .35)
currentTerm = 0
votedFor = ""
Log = []
Heartbeat = .1
isLeader = False
name = os.environ['NAME']
nodes = ["Node1", "Node2"]
currentLeader = ""
state = "follower"
beat_time = 0

# Function to decode different message types
def message_handler(msg):
    # Check time since last heartbeat & signal timeout if needed
    global beat_time
    new_time = time.perf_counter()
    if new_time - beat_time > Timeout:
        print("TIMEOUT!!!")
    
    # APPEND_RPC
    if 'leaderId' in msg:
        # Heartbeat received, refresh timeout
        if msg['Entries'] == []:
            beat_time = time.perf_counter()
    else:
        print("I can't do that yet")
            
# Listener
def listener(skt):
    print(f"Starting Listener ")
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
        except:
            # Timeout functionality if no messages received 
            if beat_time != 0 and beat_time - time.perf_counter() > Timeout:
                print("TIMEOUT!!!")
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")
        
        # Decoding the Message received from leader
        decoded_msg = json.loads(msg.decode('utf-8'))
        print(f"Message Received : {decoded_msg} From : {addr}")
        threading.Thread(target=message_handler, args=[decoded_msg]).start()

    print("Exiting Listener Function")

def heartbeat(skt):
    append_rpc = {"leaderId": name, "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        if isLeader:
            time.sleep(Heartbeat)
            for node in nodes:
                if node != name:
                    skt.sendto(json.dumps(append_rpc).encode(), (node, 5555))
                    print("sent to " + node)

if __name__ == "__main__":
    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((str(name), 5555))
    # Set timeout for socket if hasn't gotten any messages
    UDP_Socket.settimeout(Timeout)
    
    # Starting heartbeat and listener
    if name == "Node1":
        isLeader = True
    threading.Thread(target=listener, args=[UDP_Socket]).start()
    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()

