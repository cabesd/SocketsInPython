# first of all import the socket library
import socket
import argparse


def run_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0' #socket.gethostname()
    port = 9999
    s.connect((host, port))
    msg = s.recv(1024)
    print(msg.decode('ascii'))
    s.close()


def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
    host = '0.0.0.0' #socket.gethostname()
    port = 9999
    s.bind((host, port))
    print("socket binded to %s" % (port))

    s.listen(5)
    print("socket is listening")
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        msg = "Thank you for connecting"
        c.send(msg.encode("ascii"))
        c.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='Run server', action='store_true')
    args = parser.parse_args()

    if args.server:
        run_server()
    else:
        run_client()
