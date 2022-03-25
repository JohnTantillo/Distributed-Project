import socket
import time
import threading
import json
import traceback
timeout = 3
# Listener
def listener(skt):
    print(f"Starting Listener ")
    start_time = 0
    while True:
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
        if start_time != 0 and stop_time - start_time > timeout:
            print("TIMEOUT!!!")

        # if decoded_msg['counter'] >= 4:
        #     break

    print("Exiting Listener Function")

# Dummy Function
def function_to_demonstrate_multithreading():
    for i in range(5):
        print(f"Hi Executing Dummy function : {i}")
        time.sleep(2)


if __name__ == "__main__":
    print(f"Starting Node 2")

    sender = "Node2"

    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((sender, 5555))

    #Starting thread 1
    threading.Thread(target=listener, args=[UDP_Socket]).start()

    #Starting thread 2
    threading.Thread(target=function_to_demonstrate_multithreading).start()

    print("Started both functions, Sleeping on the main thread for 10 seconds now")
    time.sleep(10)
    print(f"Completed Node Main Thread Node 2")
