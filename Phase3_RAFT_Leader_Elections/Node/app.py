import time
import socket
import json
import threading
import traceback
import subprocess
import os

# Listener
def listener(skt):
    print(f"Starting Listener ")
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
        except:
            print(f"ERROR while fetching from socket : {traceback.print_exc()}")
        # Decoding the Message received from Node 1
        decoded_msg = json.loads(msg.decode('utf-8'))
        print(f"Message Received : {decoded_msg} From : {addr}")

def heartbeat(skt):
    # target = "Node2"
    append_rpc = {"leaderId": f"Node", "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        time.sleep(1)
        skt.sendto(json.dumps(append_rpc).encode(), ('localhost', 5555))
        print("sent")

if __name__ == "__main__":
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_Socket.bind(('localhost', 5555))
    # if HOST == "Node1":
    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()
    # else:
    threading.Thread(target=listener, args=[UDP_Socket]).start()
