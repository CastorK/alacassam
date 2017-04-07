import socket, select, string
import sys # for exit

class Chat_server:
    def __init__(self):
        port = 6667
        self.pingmsg = "alacazzzzzzammmm" # 6 Z & 4 M
        self.connections = []
        self.clients = []
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
                                if not self.handle_message(received, current_socket):
                                    self.broadcast(received, current_socket)

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
            client = Client(socket=sender)
            self.clients.append(client)
            message = 'Client IP: %s, PORT: %s joined' % (sender.getsockname()[0], sender.getsockname()[1])
            self.broadcast(message + '\r\n', sender)
            print message
            return True
        elif message.find('NICK ') == 0:
            print "# DEBUG # NICK command received"
            for client in self.clients:
                print '# DEBUG # USERNAME: ' + client.username
                if sender is client.socket:
                    client.username = message.split()[1]
                    print('He is called ' + client.username)
        else:
            return False

    def handle_server_command(self, command):
        command = command.strip()
        if command == 'quit':
            self.quit()


    def quit(self):
        for sock in self.connections:
            sock.close()
        sys.exit()

class Channel:
    def __init__(self, name):
        self.name = name
        self.clients = []

class Client:
    def __init__(self, socket, username='', channel=''):
        self.username = username
        self.socket = socket
        self.channel = channel

if __name__ == "__main__":
    try:
        server = Chat_server()
    except socket.error, e:
        sys.exit()
