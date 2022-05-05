import json
import socket
import traceback
import time
import threading

leader = ""

def message_handler(msg, skt):
    request = msg['request']
    if request == "LEADER_INFO":
        global leader 
        leader = msg['value']
        # msg['sender_name'] = sender
        # msg['request'] = "STORE"
        # msg['key'] = 'K1'
        # msg['value'] = 'This is NOT the message'
        # skt.sendto(json.dumps(msg).encode(), (leader, 5555))

    elif request == "RETRIEVE":
        print(msg['value'])

def listener(skt):
    print('starting listener')
    while True:
        try:
            msg, addr = skt.recvfrom(1024)
            # Decoding the Message received from leader
            decoded_msg = json.loads(msg.decode('utf-8'))
            # print(f"Message Received : {decoded_msg} From : {addr}")
            threading.Thread(target=message_handler, args=[decoded_msg, skt]).start()
        except:
            # Timeout functionality if no messages received 
            a = 1

if __name__ == "__main__":
    # Wait following seconds below sending the controller request
    time.sleep(5)

    # Read Message Template
    msg = json.load(open("Message.json"))
    msg2 = json.load(open("Message.json"))
    msg3 = json.load(open("Message.json"))
    msg4 = json.load(open("Message.json"))
    msg5 = json.load(open("Message.json"))


    # Initialize
    sender = "Controller"
    target = "Node1"
    port = 5555

    # Request
    msg['sender_name'] = sender
    msg['request'] = "STORE"
    msg['key'] = 'K1'
    msg['value'] = 'This is the message'

    msg2['sender_name'] = sender
    msg2['request'] = "STORE"
    msg2['key'] = 'K2'
    msg2['value'] = 'This is also the message'

    msg4['sender_name'] = sender
    msg4['request'] = "STORE"
    msg4['key'] = 'K3'
    msg4['value'] = 'message 3'

    msg5['sender_name'] = sender
    msg5['request'] = "STORE"
    msg5['key'] = 'K4'
    msg5['value'] = 'message 4'


    msg3['sender_name'] = sender
    msg3['request'] = "RETRIEVE"

    print(f"Request Created : {msg}")

      # Socket Creation and Binding
    skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    skt.bind((sender, port))

    threading.Thread(target=listener, args=[skt]).start()
    skt.sendto(json.dumps(msg5).encode(), (leader, 5555))
    time.sleep(5)
    # Send Message
    try:
        # Encoding and sending the message
        skt.sendto(json.dumps(msg).encode('utf-8'), (target, port))
        time.sleep(2)
        # if leader != '':
        skt.sendto(json.dumps(msg).encode(), (leader, 5555))
        time.sleep(2)
        skt.sendto(json.dumps(msg2).encode('utf-8'), (leader, port))
        time.sleep(2)
        skt.sendto(json.dumps(msg4).encode('utf-8'), (leader, port))
        time.sleep(2)
        skt.sendto(json.dumps(msg5).encode('utf-8'), (leader, port))
        time.sleep(2)
        skt.sendto(json.dumps(msg3).encode('utf-8'), (leader, port))
    except:
        #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
        print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")
