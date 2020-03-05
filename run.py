from threading import Thread
import socket
import argparse
import time


class Peer:
    _args = ""
    _available_commands = ['help', 'myip', 'myport', 'connect', 'list', 'terminate', 'send', 'exit']
    _input = None
    connections = []
    is_running = True
    sockets = []
    timeout = 2

    def __init__(self, port):

        # Used to get the real ip address of this machine
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 12000))
        self.my_ip = s.getsockname()[0]
        s.close()

        self.my_port = port
        # Run the server
        t = Thread(None, self.check_inbox)
        t.start()
        # Run the client
        self.run()
        exit(0)

    def run(self):
        while self.is_running:
            self._input = input(">> ")
            self._args = self._input.split(' ')
            if self._args[0] not in self._available_commands:
                print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
            else:
                getattr(self, 'func_' + self._args[0])()

    def func_help(self):
        print("Command\t\t\t\t\tDescription")
        print("help\t\t\t\t\tPulls this up.")
        print("myyp\t\t\t\t\tPrints your computer's ip address.")
        print("myport\t\t\t\t\tPrints the port this program is communicating through.")
        print("connect<destination><port>\t\tCreates new connection to specified destination at the specified port.")
        print("list\t\t\t\t\tDisplays a numbered list of connections.")
        print("terminate<connection id>\t\tTerminates connection specified by id in numbered list of connections.")
        print("send<connection_id><message>\t\tSends message to specified peer by id in numbered list of connections.")
        print("exit\t\t\t\t\tCloses all connections and terminates this process.")

    def func_myip(self):
        print(f"My IP is {self.my_ip}")

    def func_myport(self):
        print(f"My Port is {self.my_port}")

    def func_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._args[1], int(self._args[2])))
        s.setblocking(0)
        self.sockets.append(s)
        self.connections.append([self._args[1], int(self._args[2])])
        print(f"Connect {self._args}")

    def func_list(self):
        """ Print all active connections """
        print("ID\tIP Address\tPort No.")
        for i, conn in enumerate(self.connections):
            print(f"{i}:\t{conn[0]}\t{conn[1]}")

    def func_terminate(self):
        """ Close a connection specified by the connection id """
        idx = int(self._args[1])
        print("before", self.sockets)
        self.sockets[idx].close()
        self.sockets.pop(idx)
        print("after", self.sockets)
        self.connections.pop(idx)

        print(f"Terminated {self._args}")

    def func_send(self):
        """ Send a message to a specific connection id"""
        idx = int(self._args[1])
        msg = " ".join(self._args[2:])
        self.sockets[idx].send(msg.encode('ascii'))

    def func_exit(self):
        """ Close all the connections and then exit"""
        self.is_running = False

    def check_inbox(self):
        """ Where the server is hosted"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Listens to any ip on this network on specified port
        s.bind(('0.0.0.0', int(self.my_port)))
        while self.is_running:

            """ Since the connection is thrown away I might be able to get away with this"""
            s.listen(100)
            # print("Checking messages from {}".format(self.connections))
            c, addr = s.accept()
            # need to use the data in addr to add the ip and port to the list of connections
            # if they are not already inside the list of connections
            print(f"Data received {c} \n {addr}")

            msg = c.recv(100)
            print(msg.decode("ascii"))
            c.close()

        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs=1)
    args = parser.parse_args()
    Peer(args.port[0])
