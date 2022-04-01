import socket
import time
import threading
import json
import traceback
import random
import os

# Global information that will be stored in a volume
Timeout = random.uniform(.25, .4)
currentTerm = 0
voted = False
Log = []
Heartbeat = .1
name = os.environ['NAME']
nodes = ["Node1", "Node2", 'Node3', 'Node4', 'Node5']
state = "follower"
beat_time = 0
votes = 0

def start_election(skt):
    global state
    global votes
    global currentTerm
    global voted
    global Timeout
    requestVote_rpc = {'Term': currentTerm, 'candidateId': name, 'lastLogIndex': -1, 'lastLogTerm': 0}
    for node in nodes:
        if node != name:
            try:
                skt.sendto(json.dumps(requestVote_rpc).encode(), (node, 5555))
            except:
                print(node + ' is down')
    if not voted:
        voted = True
        votes = 1
    currentTerm += 1
    print('voting for myself')
    time.sleep(Timeout)
    if state == 'candidate' and votes >= 3:
        state = 'leader'
        threading.Thread(target=heartbeat, args=[UDP_Socket]).start()
        skt.settimeout(None)
        voted = False
    else:
        state = 'follower'
        voted = False
    votes = 0
    Timeout = random.uniform(.25, .4)
    skt.settimeout(Timeout)
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
            elif state == 'candidate':
                state = 'follower'
            voted = False
            beat_time = time.perf_counter()
            print('Heartbeat from ' + msg['leaderId'])

    elif 'Term' in msg:
        if currentTerm <= msg['Term'] and not voted:
            voted = True
            node = msg['candidateId']
            print("voting for " + node)
            vote_reply = {'voteReply': True}
            skt.sendto(json.dumps(vote_reply).encode(), (node, 5555))

    elif 'voteReply' in msg:
        global votes
        # print(votes)
        votes += 1

    else:
        print("I can't do that yet")
            
# Listener
def listener(skt):
    global beat_time
    global state 
    beat_time = time.perf_counter()
    print(f"Starting Listener ")
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
            # Decoding the Message received from leader
            decoded_msg = json.loads(msg.decode('utf-8'))
            # print(f"Message Received : {decoded_msg} From : {addr}")
            threading.Thread(target=message_handler, args=[decoded_msg, skt]).start()
        except:
            # Timeout functionality if no messages received 
            if time.perf_counter() - beat_time > Timeout and state == 'follower':
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
                    try:
                        skt.sendto(json.dumps(append_rpc).encode(), (node, 5555))
                    except:
                        print(node + ' is down')
                    # print("sent to " + node)

if __name__ == "__main__":
    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((name, 5555))
    # Set timeout for socket if hasn't gotten any messages
    UDP_Socket.settimeout(Timeout)
    # Starting heartbeat and listener
    threading.Thread(target=listener, args=[UDP_Socket]).start()

