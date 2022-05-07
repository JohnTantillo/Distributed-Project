import socket
import time
import threading
import json
import traceback
import random
import os

# TODO: Persist data needed for RAFT, test different controller commands
# TODO: CHANGE REPLY SO THAT ATTEMPTING TO APPEND OLDER MESSAGES DOESN'T BREAK BECAUSE OF TERM DIFFERENCE

# Global information that will be stored in a volume
Timeout = random.uniform(.35, .45)
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
current_key = 0
nextIndex = [0,0,0,0,0]
matchIndex = [0,0,0,0,0]
commitIndex = 0
lastApplied = -1
updated = False

def create_message(request_type):
    message = json.load(open("Message.json"))
    message['sender_name'] = name
    message['request'] = request_type
    message['term'] = currentTerm
    message['key'] = -1
    if request_type == 'VOTE_REQUEST':
        message['candidateId'] = name
        message['lastLogIndex'] = len(Log) - 1
        if len(Log) == 0:
            message['lastLogTerm'] = -1
        else:
            message['lastLogTerm'] = Log[-1]['Term']
    elif request_type == 'APPEND_RPC':
        message['leaderId'] = name
        message['Entries'] = []
        message['prevLogIndex'] = lastApplied
        if lastApplied == -1:
            message['prevLogTerm'] = -1
        else:
            message['prevLogTerm'] = Log[lastApplied]['Term']
        message['leaderCommit'] = commitIndex
    elif request_type == 'LEADER_INFO':
        message['key'] = 'LEADER'
        message['value'] = current_leader
    elif request_type == 'RETRIEVE':
        message['term'] = None
        message['key'] = 'COMMITED_LOGS'
        message['value'] = Log
    elif request_type == 'APPEND_REPLY':
        message['key'] = 'success'
    return message

def start_election(skt):
    global state
    global votes
    global currentTerm
    global voted
    global Timeout
    global votedFor
    global nextIndex
    global matchIndex
    message = create_message("VOTE_REQUEST")
    for node in nodes:
        if node != name:
            try:
                skt.sendto(json.dumps(message).encode(), (node, 5555))
            except:
                a = 1
    if not voted:
        voted = True
        votes = 1
        votedFor = name
    currentTerm += 1
    time.sleep(1)
    if state == 'candidate' and votes >= 3:
        matchIndex = [0,0,0,0,0]
        nextIndex = [lastApplied+1]*5
        print(nextIndex)
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

# Function to decode different message types
def message_handler(msg, skt):
    # Check time since last heartbeat & signal timeout if needed
    global beat_time
    global voted
    global state
    global current_leader
    global kill
    global lastApplied
    global commitIndex
    global Log
    global currentTerm
    new_time = time.perf_counter()
    if new_time - beat_time > Timeout and state == 'follower':
        state = 'candidate'
        threading.Thread(target=start_election, args=[skt]).start()
    
    request = msg['request']

    # APPEND_RPC
    if request == 'APPEND_RPC':
        # Heartbeat received, refresh timeout
        beat_time = time.perf_counter()
        current_leader = msg['leaderId']
        if msg['Entries'] == []:
            if state == 'leader':
                skt.settimeout(Timeout)
            elif state == 'candidate':
                if currentTerm != msg['term']:
                    currentTerm = msg['term']
                state = 'follower'
            voted = False
        else:
            if currentTerm != msg['term']:
                currentTerm = msg['term']

            if Log == [] and lastApplied == msg['prevLogIndex']:
                print('First append')
                Log.append(msg['Entries'][0])
                lastApplied += 1
                reply = create_message('APPEND_REPLY')
                reply['value'] = True
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))
                print(Log)

            elif msg['prevLogIndex'] >= len(Log):
                print("index too long")
                print(len(Log))
                print(msg['prevLogIndex'])
                reply = create_message('APPEND_REPLY')
                reply['value'] = False
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))

            elif msg['term'] < currentTerm:
                print('Message term lower than current')
                print('message: ' + str(msg))
                print('current term: ' + str(currentTerm))
                reply = create_message('APPEND_REPLY')
                reply['value'] = False
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))

            elif Log[msg['prevLogIndex']]['Term'] != msg['prevLogTerm']:
                print('Disagreement on terms')
                print('Log: ' + str(Log))
                print('msg: ' + str(msg))
                reply = create_message('APPEND_REPLY')
                reply['value'] = False
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))

            elif msg['prevLogIndex'] + 1 < len(Log):
                if Log[msg['prevLogIndex']+1]['Term'] != msg['term']:
                    Log = Log[:msg['prevLogIndex']+1]
                reply = create_message('APPEND_REPLY')
                print(Log)
                reply['value'] = True
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))

            else:
                if msg['Entries'][0] in Log:
                    return
                elif msg['prevLogIndex'] + 1 >= len(Log):
                    print('Appending')
                    Log.append(msg['Entries'][0])
                else: 
                    print('Editing')
                    Log[msg['prevLogIndex']+1] = msg['Entries'][0]
                lastApplied += 1
                print(Log)
                reply = create_message('APPEND_REPLY')
                reply['value'] = True
                skt.sendto(json.dumps(reply).encode(), (current_leader, 5555))

            if msg['leaderCommit'] > commitIndex:
                commitIndex = min(msg['leaderCommit'], lastApplied)
            
    elif request == 'VOTE_REQUEST':
        if len(Log) == 0:
            last_term = -1
        else:
            last_term = Log[-1]['Term']
        if currentTerm <= msg['term'] and (msg['lastLogTerm'] >= last_term or 
        (msg['lastLogTerm'] == last_term and msg['lastLogIndex'] >= len(Log)-1)) and not voted:
            voted = True
            node = msg['candidateId']
            vote_reply = create_message('VOTE_ACK')
            skt.sendto(json.dumps(vote_reply).encode(), (node, 5555))
            global votedFor
            votedFor = node

    elif request == 'VOTE_ACK':
        global votes
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
        reply = create_message("LEADER_INFO")
        skt.sendto(json.dumps(reply).encode(), ('Controller', 5555))
        print('The current leader is ' + current_leader)

    elif request == "STORE":
        if state == 'leader':
            lastApplied += 1
            entry = {'Term': currentTerm, 'Key': msg['key'], 'Value': msg['value']}
            Log.append(entry)
            print(Log)
        else:
            reply = create_message("LEADER_INFO")
            skt.sendto(json.dumps(reply).encode(), ('Controller', 5555))

    elif request == "RETRIEVE":
        if state == 'leader':
            reply = create_message("RETRIEVE")
        else:
            reply = create_message("LEADER_INFO")
        skt.sendto(json.dumps(reply).encode(), ('Controller', 5555))
   
    elif request == 'APPEND_REPLY':
        node_num = int(msg['sender_name'][-1])-1
        if msg['value'] == True:
            matchIndex[node_num] += 1
            nextIndex[node_num] += 1
        else: 
            if nextIndex[node_num] >= 0:
                nextIndex[node_num] -= 1
        matcher = {}
        for i in matchIndex:
            if i not in matcher:
                matcher[i] = 1
            else:
                for key in matcher:
                    if i >= matcher[key]: 
                        matcher[key] += 1
        for ind in matcher:
            if matcher[ind] >= 2 and ind > commitIndex:
                commitIndex = ind
        print("commit index: " + str(commitIndex))
        print('next index: ' + str(nextIndex))
    else:
        print("UNSUPPORTED MESSAGE TYPE, PLEASE RECONSIDER")
            
# Listener
def listener(skt):
    global beat_time
    global state 
    beat_time = time.perf_counter()
    print(f"Starting Listener ")
    while True:
        data = {"currentTerm": currentTerm, "votedFor": votedFor, "Log": [], "Timeout": Timeout, 
        'Heartbeat': Heartbeat, 'commitIndex': commitIndex, 'log': Log, 'lastApplied': lastApplied}
        if kill:
            return
        try:
            msg, addr = skt.recvfrom(1024)
            # Decoding the Message received from leader
            decoded_msg = json.loads(msg.decode('utf-8'))
            threading.Thread(target=message_handler, args=[decoded_msg, skt]).start()
        except:
            # Timeout functionality if no messages received 
            if time.perf_counter() - beat_time > Timeout and state == 'follower':
                state = 'candidate'
                threading.Thread(target=start_election, args=[skt]).start()
        data['currentTerm'] = currentTerm
        data['votedFor'] = votedFor
        with open(name+".txt", 'w') as f:
            f.write(json.dumps(data))

    print("Exiting Listener Function")

def heartbeat(skt):
    print('I am the leader')
    while True:
        data = {"currentTerm": currentTerm, "votedFor": votedFor, "Log": [], "Timeout": Timeout, 
        'Heartbeat': Heartbeat, 'commitIndex': commitIndex, 'log': Log, 'lastApplied': lastApplied}
        if kill:
            return
        if state == 'leader':
            time.sleep(Heartbeat)
            for node in nodes:
                app_rpc = create_message("APPEND_RPC")
                node_num = int(node[-1])-1
                if nextIndex[node_num] == lastApplied:
                    node_ind = lastApplied - 1
                else:
                    node_ind = nextIndex[node_num] - 1
                if node != name and node_ind < lastApplied and lastApplied >= 0:
                    app_rpc['prevLogIndex'] = node_ind
                    app_rpc['prevLogTerm'] = Log[node_ind]['Term']
                    app_rpc['Entries'].append(Log[node_ind+1])
                if node != name:
                    try:
                        skt.sendto(json.dumps(app_rpc).encode(), (node, 5555))
                    except:
                        a = 1
            with open(name+".txt", 'w') as f:
                f.write(json.dumps(data))

if __name__ == "__main__":
    with open(name+".txt", 'r') as f:
        info = f.read()
        print(info)
    if info != '':
        info = json.loads(info)
        Timeout = info['Timeout']
        currentTerm = info['currentTerm']
        votedFor = info['votedFor']
        commitIndex = info['commitIndex']
        lastApplied = info['lastApplied']
        Log = info['log']
    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((name, 5555))
    # Set timeout for socket if hasn't gotten any messages
    UDP_Socket.settimeout(Timeout)
    # Starting heartbeat and listener
    threading.Thread(target=listener, args=[UDP_Socket]).start()

