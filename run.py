from threading import Thread
import socket
import argparse
import time


class peer():
    is_running = True
    _input = None
    _available_commands = ['help', 'myip', 'myport', 'connect', 'list', 'terminate', 'send', 'exit']
    connections = []
    timeout = 2

    def __init__(self, port):

        # Used to get the real ip address of this machine
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 12000))
        self.myip = s.getsockname()[0]
        s.close()

        self.myport = port
        # self.open_socket()

        # I guess this is the server
        t = Thread(None, self.check_inbox)
        t.start()
        self.run()

    def run(self):
        while self.is_running:
            self._input = input(">> ")
            self._args = self._input.split(' ')
            if self._args[0] not in self._available_commands:
                print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
            else:
                getattr(self, 'func_' + self._args[0])()

    def func_help(self):
        print("Show help message")

    def func_myip(self):
        print(f"My IP is {self.myip}")

    def func_myport(self):
        print(f"My port is {self.myport}")

    def func_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self._args)
        s.connect((self._args[1], int(self._args[2])))
        self.connections.append(s)
        print(f"Connect {self._args}")

    def func_list(self):
        print(f"Show Connection List\n{self.connections}")

    def func_terminate(self):
        print(f"Terminate {self._args}")

    def func_send(self):
        print(f"Send {self._args}")

    def func_exit(self):
        '''TODO Send message to connections so they update their connections list'''
        self.is_running = False

    def open_socket(self):
        pass

    def check_inbox(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', int(self.myport)))
        while self.is_running:

            # I think here we want to be able to accept as many connections as possible

            s.listen(1024)
            print("Checking messages from {}".format(self.connections))
            time.sleep(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs=1)
    args = parser.parse_args()
    peer(args.port[0])
