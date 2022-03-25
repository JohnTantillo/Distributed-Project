import time
import socket
import json
import threading
import traceback

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

        # if decoded_msg['counter'] >= 4:
        #     break

    print("Exiting Listener Function")

# Dummy Function
def function_to_demonstrate_multithreading():
    for i in range(5):
        print(f"Hi Executing Dummy function : {i}")
        time.sleep(2)

def create_msg(counter):
    msg = {"msg": f"Hi, I am Node", "counter":counter}
    msg_bytes = json.dumps(msg).encode()
    return msg_bytes

def heartbeat(skt):
    target = "Node2"
    append_rpc = {"leaderId": f"Node", "Entries":[], "prevLogIndex":-1, "prevLogTerm":-1}
    while True:
        time.sleep(1)
        skt.sendto(json.dumps(append_rpc).encode(), (target, 5555))
        print("sent")

if __name__ == "__main__":

    sender = "Node1"
    target = "Node2"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_Socket_2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))
    sender = "Node2"
    UDP_Socket_2.bind((sender, 5555))
    #Starting thread 1
    threading.Thread(target=listener, args=[UDP_Socket_2]).start()

    #Starting thread 2
    # threading.Thread(target=function_to_demonstrate_multithreading).start()

    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()

