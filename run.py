from threading import Thread
import socket, argparse, time

class peer():
    is_running = True
    myip = '127.0.0.1'
    myport = None
    _input = None
    _available_commands = ['help', 'myip', 'myport', 'connect', 'list', 'terminate', 'send', 'exit']
    connections = []
    timeout = 2

    def __init__(self, port):
        self.myport = port
        self.open_socket()

        t = Thread(None, self.check_inbox)
        t.start()
        self.run()
        t.cancel()

    def run(self):
        while self.is_running:
            self._input = input(">> ")
            self._args = self._input.split(' ')
            if self._args[0] not in self._available_commands:
                print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
            else:
                getattr(self, 'func_'+self._args[0])()


    def func_help(self):
        print("Show help message")

    def func_myip(self):
        print("My IP is {}".format(self.myip))

    def func_myport(self):
        print("My port is {}".format(self.myport))

    def func_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections.append(s)
        print("Connect {}".format(self._args))

    def func_list(self):
        print("Show Connection List\n{}".format(self.connections))

    def func_terminate(self):
        print("Terminate {}".format(self._args))

    def func_send(self):
        print("Send {}".format(self._args))

    def func_exit(self):
        '''TODO Send message to connections so they update their connections list'''
        self.is_running = False

    def open_socket(self):
        pass

    def check_inbox(self):
        while self.is_running:
            print("Checking messages from {}".format(self.connections))
            time.sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs=1)
    args = parser.parse_args()
    peer(args.port[0])