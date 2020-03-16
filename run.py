from threading import Thread
import socket
import argparse
import selectors
import types



class Peer:
    _args = ""
    _available_commands = ['help', 'myip', 'myport', 'connect', 'list', 'terminate', 'send', 'exit']
    _input = None
    connections = []
    is_running = True
    sockets = []
    timeout = 2

    def __init__(self, port):

        self.client_sel = selectors.DefaultSelector()
        self.server_sel = selectors.DefaultSelector()

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

    def run(self):
        try:
            while self.is_running:
                # events = self.client_sel.select(timeout=1)
                self._input = input(">> ")
                self._args = self._input.split(' ')
                if self._args[0] not in self._available_commands:
                    print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
                else:
                    getattr(self, 'func_' + self._args[0])()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.client_sel.close()

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
        addr = (self._args[1], int(self._args[2]))
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        self.sockets.append(sock)
        self.connections.append(addr)

    def func_list(self):
        """ Print all active connections """
        print("ID\tIP Address\tPort No.")
        for i, conn in enumerate(self.connections):
            print(f"{i}:\t{conn[0]}\t{conn[1]}")

    def func_terminate(self, idx=False):
        """ Close a connection specified by the connection id """
        # When a peer terminates their connection
        if not idx:
            idx = int(self._args[1])
            term_msg = f"{self.my_ip} has terminated their connection."
            self.sockets[idx].send(term_msg)
        # When the server terminates a connection
        self.sockets[idx].close()
        self.sockets.pop(idx)
        self.connections.pop(idx)

        print(f"Terminated {self._args}")

    def service_client_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                print("received", repr(recv_data), "from connection", data.connid)
                data.recv_total += len(recv_data)
            if not recv_data or data.recv_total == data.msg_total:
                print("closing connection", data.connid)
                self.client_sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                print("sending", repr(data.outb), "to connection", data.connid)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def func_send(self):
        idx = int(self._args[1])
        message = " ".join(self._args[2:])

        data = types.SimpleNamespace(
            connid=idx,
            msg_total=len(message),
            recv_total=0,
            messages=list(message.encode('utf-8')),
            outb=b"",
        )

        self.client_sel.register(self.sockets[idx], selectors.EVENT_WRITE, data=data)

        events = self.client_sel.select(timeout=1)
        for key, mask in events:
            self.service_client_connection(key, mask)

    def func_exit(self):
        """ Close all the connections and then exit"""
        # close all the sockets
        for s in self.sockets:
            s.close()
        self.is_running = False
        exit(0)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.server_sel.register(conn, events, data=data)

    def service_server_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            else:
                print("closing connection to", data.addr)
                self.server_sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print("echoing", repr(data.outb), "to", data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def check_inbox(self):
        """ Where the server is hosted"""

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind(('0.0.0.0', int(self.my_port)))
        lsock.listen()
        lsock.setblocking(False)
        self.server_sel.register(lsock, selectors.EVENT_READ, data=None)
        try:
            while self.is_running:
                events = self.server_sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_server_connection(key, mask)
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.server_sel.close()
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs=1)
    args = parser.parse_args()
    Peer(args.port[0])
