import socket
import time
import threading
import json
import traceback
import random
import os

# TODO: Persist data needed for RAFT, test different controller commands

# Global information that will be stored in a volume
Timeout = random.uniform(.25, .4)
current_leader = ""
currentTerm = 0
voted = False
votedFor = ""
Log = []
Heartbeat = .1
name = os.environ['NAME']
nodes = ["Node1", "Node2", 'Node3', 'Node4', 'Node5']
state = "follower"
beat_time = 0
votes = 0
kill = False

def create_message(request_type):
    message = json.load(open("Message.json"))
    message['sender_name'] = name
    message['request'] = request_type
    message['term'] = currentTerm
    if request_type == 'VOTE_REQUEST':
        message['Term'] = currentTerm
        message['candidateId'] = name
        message['lastLogIndex'] = -1
        message['lastLogTerm'] = -1
    elif request_type == 'APPEND_RPC':
        message['leaderId'] = name
        message['Entries'] = []
        message['prevLogIndex'] = -1
        message['prevLogTerm'] = -1
    return message

def start_election(skt):
    global state
    global votes
    global currentTerm
    global voted
    global Timeout
    global votedFor
    message = create_message("VOTE_REQUEST")
    for node in nodes:
        if node != name:
            try:
                skt.sendto(json.dumps(message).encode(), (node, 5555))
            except:
                print(node + ' is down')
    if not voted:
        voted = True
        votes = 1
        votedFor = name
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
    global current_leader
    global kill
    new_time = time.perf_counter()
    if new_time - beat_time > Timeout and state == 'follower':
        state = 'candidate'
        print("Starting Election")
        threading.Thread(target=start_election, args=[skt]).start()
    
    request = msg['request']

    # APPEND_RPC
    if request == 'APPEND_RPC':
        # Heartbeat received, refresh timeout
        if msg['Entries'] == []:
            if state == 'leader':
                skt.settimeout(Timeout)
            elif state == 'candidate':
                state = 'follower'
            voted = False
            beat_time = time.perf_counter()
            current_leader = msg['leaderId']
            print('Heartbeat from ' + msg['leaderId'])

    elif request == 'VOTE_REQUEST':
        if currentTerm <= msg['Term'] and not voted:
            voted = True
            node = msg['candidateId']
            print("voting for " + node)
            vote_reply = create_message('VOTE_ACK')
            skt.sendto(json.dumps(vote_reply).encode(), (node, 5555))
            global votedFor
            votedFor = node

    elif request == 'VOTE_ACK':
        global votes
        # print(votes)
        votes += 1

    elif request == 'CONVERT_FOLLOWER':
        state = 'follower'
        if kill:
            kill = False
            threading.Thread(target=listener, args=[UDP_Socket]).start()
    
    elif request == 'TIMEOUT':
        state = 'candidate'
        threading.Thread(target=start_election, args=[skt]).start()
   
    elif request == "SHUTDOWN":
        kill = True

    elif request == "LEADER_INFO":
        if state == 'leader':
            current_leader = name
        print('The current leader is ' + current_leader)
        return {'LEADER':current_leader}

    else:
        print("UNSUPPORTED MESSAGE TYPE, PLEASE RECONSIDER")
            
# Listener
def listener(skt):
    global beat_time
    global state 
    beat_time = time.perf_counter()
    print(f"Starting Listener ")
    while True:
        if kill:
            return
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
    beat = create_message('APPEND_RPC')
    while True:
        if kill:
            return
        if state == 'leader':
            time.sleep(Heartbeat)
            for node in nodes:
                if node != name:
                    try:
                        skt.sendto(json.dumps(beat).encode(), (node, 5555))
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

