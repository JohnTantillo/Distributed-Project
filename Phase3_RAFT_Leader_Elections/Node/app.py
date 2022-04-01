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
voted = False
Log = []
Heartbeat = .1
name = os.environ['NAME']
nodes = ["Node1", "Node2", 'Node3']
state = "follower"
beat_time = 0
votes = 0

def start_election(skt):
    global state
    global votes
    global currentTerm
    global voted
    voted = True
    votes = 1
    currentTerm += 1
    requestVote_rpc = {'Term': currentTerm, 'candidateId': name, 'lastLogIndex': -1, 'lastLogTerm': 0}
    for node in nodes:
        if node != name:
            skt.sendto(json.dumps(requestVote_rpc).encode(), (node, 5555))
            print("sent to " + node)
    while votes < 2 and state == 'candidate':
        temp = 1
        time.sleep(.5)
        # print('waiting for votes')
    if state == 'candidate':
        state = 'leader'
        threading.Thread(target=heartbeat, args=[UDP_Socket]).start()
        skt.settimeout(None)
        voted = False
    votes = 0
    print("Ending Election")

# Function to decode different message types
def message_handler(msg, skt):
    # Check time since last heartbeat & signal timeout if needed
    global beat_time
    global voted
    global state
    new_time = time.perf_counter()
    if new_time - beat_time > Timeout and state == 'follower':
        state = 'candidate'
        print("Starting Election")
        threading.Thread(target=start_election, args=[skt]).start()
    
    # APPEND_RPC
    if 'leaderId' in msg:
        # Heartbeat received, refresh timeout
        if msg['Entries'] == []:
            if state == 'leader':
                skt.settimeout(Timeout)
            state = 'follower'
            voted = False
            beat_time = time.perf_counter()

    elif 'Term' in msg:
        if currentTerm <= msg['Term'] and not voted:
            voted = True
            node = msg['candidateId']
            print("voting for " + node)
            vote_reply = {'voteReply': True}
            skt.sendto(json.dumps(vote_reply).encode(), (node, 5555))

    elif 'voteReply' in msg:
        global votes
        print(votes)
        votes += 1

    else:
        print("I can't do that yet")
            
# Listener
def listener(skt):
    global beat_time
    beat_time = time.perf_counter()
    print(f"Starting Listener ")
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
            # Decoding the Message received from leader
            decoded_msg = json.loads(msg.decode('utf-8'))
            print(f"Message Received : {decoded_msg} From : {addr}")
            threading.Thread(target=message_handler, args=[decoded_msg, skt]).start()
        except:
            # Timeout functionality if no messages received 
            if beat_time != 0 and beat_time - time.perf_counter() > Timeout and state == 'follower':
                state = 'candidate'
                threading.Thread(target=start_election, args=[skt]).start()
            # print(f"ERROR while fetching from socket : {traceback.print_exc()}")

    print("Exiting Listener Function")

def heartbeat(skt):
    append_rpc = {"leaderId": name, "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        if state == 'leader':
            time.sleep(Heartbeat)
            for node in nodes:
                if node != name:
                    skt.sendto(json.dumps(append_rpc).encode(), (node, 5555))
                    print("sent to " + node)

if __name__ == "__main__":
    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((name, 5555))
    # Set timeout for socket if hasn't gotten any messages
    UDP_Socket.settimeout(Timeout)

    # Starting heartbeat and listener
    threading.Thread(target=listener, args=[UDP_Socket]).start()

