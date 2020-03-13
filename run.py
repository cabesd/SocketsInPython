from threading import Thread
import socket
import argparse
import time
import selectors
import libserver
import libclient
import traceback

sel = selectors.DefaultSelector()


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

    def run(self):

        try:
            while self.is_running:
                events = sel.select(timeout=1)
                self._input = input(">> ")
                self._args = self._input.split(' ')
                if self._args[0] not in self._available_commands:
                    print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
                else:
                    getattr(self, 'func_' + self._args[0])()

                for key, mask in events:
                    message = key.data
                    try:
                        # This is the part that outputs the message that we received
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()

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

    def create_request(self, action, value):
        if action == "message":
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value),
            )
        else:
            return dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(action + value, encoding="utf-8"),
            )

    def func_connect(self):

        # this part seems to need a little more
        # I think it was designed to be search and then what we're searching for
        # but we want to make it useable for a simple chat application
        request = self.create_request("message", "first message")

        addr = (self._args[1], int(self._args[2]))
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(sel, sock, addr, request)
        sel.register(sock, events, data=message)
        self.sockets.append(sock)
        self.connections.append((addr[0], int(addr[1])))

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

    def func_send(self):

        # I added this, it may not belong
        events = sel.select(timeout=1)

        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # # Check for a socket being monitored to continue.
        # This also may be necessary
        # if not sel.get_map():
        #     break

        # """ Send a message to a specific connection id"""
        # idx = int(self._args[1])
        # msg = " ".join(self._args[2:])
        #
        # self.sockets[idx].send(msg.encode('ascii'))

    def func_exit(self):
        """ Close all the connections and then exit"""
        # close all the sockets
        for s in self.sockets:
            s.close()
        self.is_running = False
        exit(0)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = libserver.Message(sel, conn, addr)
        sel.register(conn, selectors.EVENT_READ, data=message)

    def check_inbox(self):
        """ Where the server is hosted"""
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind(('0.0.0.0', int(self.my_port)))
        lsock.listen()
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while self.is_running:

                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            sel.close()
        exit(0)

    #     """ Since the connection is thrown away I might be able to get away with this"""
    #     # print("after listen")
    #     # print("Checking messages from {}".format(self.connections))
    #     try:
    #         # print("before accept")
    #         c, addr = s.accept()
    #         # print("after accept")
    #         # print(f"Data received {c} \n {addr}")
    #         # if addr is not None and (c, addr) not in self.sockets:
    #         #     self.connections.append([addr[0], addr[1]])
    #         #     self.sockets.append(s)
    #         #     addr = None
    #     except Exception as e:
    #             print(e)
    #     else:
    #         # print("before recv")
    #         msg = c.recv(100).decode("ascii")
    #         # print("after recv")
    #         if msg:
    #             print(f"Message received from {addr[0]}")
    #             print(f"Sender's Port: {addr[1]}")
    #             print(f"Message: {msg}")
    #         """
    #         There may be use case here for this, not sure yet
    #         I'm imagining parsing the messages from other peers
    #         to call certain functions.
    #         """
    #         if "terminated" in msg:
    #             idx = self.connections.index(addr[0])
    #             getattr(self, 'func_' + self._args[0])(idx)
    #
    #         # if self._args[0] not in self._available_commands:
    #         #     print("Invalid command '{}' - type 'help' to get the available commands".format(self._input))
    #         # else:
    #     finally:
    #         # theory one, maybe i do need to close the connection each time?
    #         pass
    # # need to use the data in addr to add the ip and port to the list of connections
    # # if they are not already inside the list of connections
    #
    # exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", nargs=1)
    args = parser.parse_args()
    Peer(args.port[0])
