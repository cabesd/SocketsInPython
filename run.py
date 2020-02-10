# first of all import the socket library
import socket, argparse, time

def run_client():
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
            print("Message lenght = 0")
            pass
    print(msg.decode('ascii'))
    s.close()

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
    host = '0.0.0.0' #socket.gethostname()
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
    parser.add_argument('--server', help='Run server', action='store_true')
    args = parser.parse_args()

    if args.server:
        run_server()
    else:
        run_client()