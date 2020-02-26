import socket
import time
import threading
import argparse


'''
    Thoughts/Ideas

    Each user could technically create their own chat room but we're handling the base case where there is only
    one chat room.
    
    connection process I am imagining
        
        In this case the user that initiated the chat room would have three processes and anyone connecting
        would have two processes.
        
        user 0 creates the server
        user 0 joins the server as a client
            - has a process to host server
            - process to listen for messages from the server and writes them to the terminal
            - process that listens to the user and transmits the messages/commands to the server
        user 1 joins the server as a client
            - process to listens for messages from the server and writes them to the terminal
            - process that listens to the user and transmits the messages/commands to the server
        user 2 joins the server as a client
            - process to listens for messages from the server and writes them to the terminal
            - process to that listens to the user and transmits the message/commands to the server
        
'''

'''

    When the server gets gains or loses a connection it should output a message to everyone.

    Process that's listening will look for particular words that would indicate that something important happened
    that would require an action on its part:
        - a user exited the chat
            - process would have to add the user to its local list of connections
        - a user entered the chat
            - process would have to remove the user from its local list of connections
            
'''

'''

    - When users connect should they have to check if the chat room exists already?
    
    - What happens if you have two servers listening to the same port? 
    
    - Would they both get the message?
    
    - Would it detect that there is already a process running on that port?
    
    - Would the user who initiated the chat room have a different ip address for each of the processes?
    
    - Would it be the same?
    
'''


class ChatRoomClient:

    def __init__(self):
        # When this process is spawned, it should block until it gets the current state of chat to populate its data
        pass

    def help(self):
        pass

    def client_ip(self):
        pass

    def client_port(self):
        pass

    def connect(self, dest, port):
        pass

    def list(self):
        pass

    def terminate(self):
        pass

    def send(self, msg):
        pass

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '0.0.0.0' #socket.gethostname()
        port = 9990
        s.connect((host, port))
        s.setblocking(0)
        msg = ''
        while len(msg) == 0:
            try:
                msg = s.recv(1024)
                break
            except BlockingIOError:
                print("Message length = 0")
                pass
        print(msg.decode('ascii'))
        s.close()


class ChatRoomServer:

    def __init__(self):
        pass

    def run(self):
        pass

    def help(self):
        pass

    def server_ip(self):
        pass

    def server_port(self):
        pass

    def list(self):
        pass

    def terminate(self):
        pass

    def send(self, msg):
        pass

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
        host = '0.0.0.0' # socket.gethostname()
        port = 9990
        s.bind((host, port))
        print("socket binded to %s" % (port))

        s.listen(5)
        print("socket is listening")
        while True:
            c, addr = s.accept()
            print('Got connection from', addr)
            data = {'test': 'msg'}
            msg = str(data)
            time.sleep(2)
            c.send(msg.encode("ascii"))
            c.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', help='Run server', required=True, action='store_true')
    args = parser.parse_args()

    if args.server:
        server = ChatRoomServer()
        print("server woudl have ran")
        server.run()
        exit(0)
    else:
        client = ChatRoomClient()
        print("client would have ran")
        exit(0)
        client.run()
