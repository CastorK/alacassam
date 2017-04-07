import socket, select, string
import sys # for exit

class style:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Chat_server:
    def __init__(self):
        port = 6667
        self.pingmsg = "alacazzzzzzammmm" # 6 Z & 4 M
        self.connections = []
        self.connected_clients = []
        self.pendingConnections = []
        try:
            # IPv4 TCP socket
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Socket can reuse address, this is to prevent the "Address already in use" error message
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind socket to port
            #server.bind((socket.gethostbyname(socket.gethostname()), port))
            self.server.bind(('', port))
            # Listen for connections, max 5 connections in queue
            self.server.listen(5)
            # Add server to list of readable sockets
            self.connections.append(self.server)
            print 'Alacassam chat server started on port %s' % port
            # Do stuff with connections
            while True:
                # Blocks until at least one file descriptor is ready.
                # 30 second timeout on blocking.
                # We're only interested in reading incoming connections
                # (eg. new connections or messages from a client)

                read, write, error = select.select(self.connections + self.pendingConnections + [sys.stdin], [], [], 30)

                for current_socket in read:
                    # A try-except here can catch errors caused by a broken client socket,
                    # without interrupting the server
                    try:
                        # If the server socket has changed, it has registered a new connection
                        if current_socket == self.server:
                            # Accept the new connection, save the client socket and address
                            client, address = self.server.accept()
                            self.pendingConnections.append(client)
                            clientObject = Client(socket=client)
                            self.connected_clients.append(clientObject)
                            self.ping(client)

                        elif current_socket == sys.stdin:
                            received = sys.stdin.readline()
                            self.handle_server_command(received)
                        # Message from client
                        else:
                            # TODO: Check if the whole message has been received
                            received = current_socket.recv(4096)

                            # Some data was received
                            if received:
                                # TODO: Add sender name to message
                                for message in received.split('\r\n'):
                                    if not self.handle_message(message.strip(), current_socket):
                                        self.broadcast(message.strip(), current_socket)


                            # Probably a broken socket
                            else:
                                if current_socket in self.connections:
                                    self.connections.remove(current_socket)

                                message = 'Client IP: %s, PORT: %s has disconnected' % address
                                self.broadcast(message + '\r\n', current_socket)
                                print message

                    except socket.error, msg:
                        message = 'Client IP: %s, PORT: %s has disconnected' % address
                        self.broadcast(message + '\r\n', current_socket)
                        print 'Error code: %s\nError message : %s' % (str(msg[0]), msg[1])
                        print message
                        continue

            server.close()

        except socket.error, msg:
            print ('Error code: %s\nError message : %s' % (str(msg[0]), msg[1]))
            sys.exit();

    # Send message to all connected clients, except for the one who sent the message
    def broadcast(self, message, sender_socket):
        for socket in self.connections:
            try:
                if socket != self.server and socket != sender_socket:
                    # TODO: Check that the whole message has been sent.
                    socket.send(message)
            except :
                # Socket is broken
                socket.close()
                if socket in self.connections:
                    self.connections.remove(socket)

    def ping(self, client):
        if client in self.pendingConnections:
            try:
                client.send('PING :' + self.pingmsg + '\r\n')
            except:
                client.close()
                self.pendingConnections.remove(client)

    def handle_message(self, message, sender):
        if message.find('PONG') == 0 and sender in self.pendingConnections:
            self.pendingConnections.remove(sender)  # Remove socket from unauthorized connections
            self.connections.append(sender)         # Add it to authorized connections
            message = 'Client IP: %s, PORT: %s joined' % (sender.getsockname()[0], sender.getsockname()[1])
            self.broadcast(message + '\r\n', sender)
            print message
            return True
        elif message.find('NICK ') == 0:
            for client in self.connected_clients:
                if sender is client.socket:
                    client.username = message.split()[1]
                    print 'Client IP: %s, PORT: %s is now called %s' % (sender.getsockname()[0], sender.getsockname()[1], client.username)
            return True
        elif message.find('JOIN ') == 0:
            for client in self.connected_clients:
                if sender is client.socket:
                    client.channel = '#' + message.split()[1]
                    print 'Client IP: %s, PORT: %s joined %s' % (sender.getsockname()[0], sender.getsockname()[1], client.channel)
            return True
        else:
            return False

    # Function for handling commands given to the server via stdin
    def handle_server_command(self, command):
        command = command.strip().split(':')
        key = command[0]
        argument = command[1].strip() if len(command) > 1 else None

        if key == 'quit':
            self.quit()
        elif key == 'broadcast':
            if argument:
                self.broadcast(style.PURPLE + style.BOLD + 'server:' + style.END + argument, self.server)

    def quit(self):
        for sock in self.connections:
            sock.close()
        sys.exit()

class Channel:
    def __init__(self, name):
        self.name = name
        self.clients = []

class Client:
    def __init__(self, socket, username=None, channel=None):
        self.socket = socket
        if username is None:
            self.username = ''
        else:
            self.username = username
        if channel is None:
            self.channel = ''
        else:
            self.channel = channel

if __name__ == "__main__":
    try:
        server = Chat_server()
    except socket.error, e:
        sys.exit()
