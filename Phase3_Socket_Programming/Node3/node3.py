import socket
import time
import threading
import json
import traceback
timeout = 3
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
        # if decoded_msg['prevLogIndex'] == -1:
        #     start_time = time.perf_counter()
        # stop_time = time.perf_counter()
        # print(str(stop_time-start_time))
        # if stop_time - start_time > timeout:
        #     print("TIMEOUT!!!")

        # if decoded_msg['counter'] >= 4:
        #     break

    print("Exiting Listener Function")

def heartbeat(skt):
    target = "Node2"
    append_rpc = {"leaderId": f"Node3", "Entries":[], "prevLogIndex":0, "prevLogTerm":-1}
    while True:
        time.sleep(5)
        skt.sendto(json.dumps(append_rpc).encode(), (target, 5555))
        print("sent")

if __name__ == "__main__":
    print(f"Starting Node 2")

    sender = "Node3"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    #Starting thread 1
    threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2
    threading.Thread(target=heartbeat, args=[UDP_Socket]).start()

    print("Started both functions, Sleeping on the main thread for 10 seconds now")
    time.sleep(10)
    print(f"Completed Node Main Thread Node 2")
