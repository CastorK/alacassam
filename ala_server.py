import socket, select
import sys # for exit

def chat_server():
    port = 9001
    connections = []

    try:
        # IPv4 TCP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Socket can reuse address, this is to prevent the "Address already in use" error message
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to port
        # server.bind((socket.gethostname(), port))
        server.bind(('', port))

        # Listen for connections, max 5 connections in queue
        server.listen(5)

        # Add server to list of readable sockets
        connections.append(server)

        print ('Alacassam chat server started on port %s' % port)

        # Do stuff with connections
        while True:
            # Blocks until at least one file descriptor is ready.
            # 30 second timeout on blocking.
            # We're only interested in reading incoming connections
            # (eg. new connections or messages from a client)
            read, write, error = select.select(connections, [], [], 30)

            for current_socket in read:
                # A try-except here can catch errors caused by a broken client socket,
                # without interrupting the server
                try:
                    # If the server socket has changed, it has registered a new connection
                    if current_socket == server:
                        # Accept the new connection, save the client socket and address
                        client, address = server.accept()
                        connections.append(client)
                        print ('Client IP: %s, PORT: %s joined' % address)
                    # Message from client
                    else:
                        # TODO: Check if the whole message has been received
                        received = current_socket.recv(4096)

                        # Some data was received
                        if received:
                            # TODO: Add sender name to message
                            send_to_all(received, server, current_socket, connections)

                        # Probably a broken socket
                        else:
                            if current_socket in connections:
                                connections.remove(current_socket)
                                
                            message = 'Client IP: %s, PORT: %s has disconnected' % address
                            send_to_all(message, server, current_socket)

                except:
                    message = 'Client IP: %s, PORT: %s has disconnected' % address
                    send_to_all(message, server, current_socket)
                    continue

        server.close()

    except socket.error, msg:
        print ('Error code: %s\nError message : %s' % (str(msg[0]), msg[1]))
        sys.exit();

# Send message to all connected clients, except for the one who sent the message
def send_to_all(message, server, sender_socket, connections):
    for socket in connections:
        try:
            if socket != server and socket != sender_socket:
                # TODO: Check that the whole message has been sent.
                socket.send(message)
        except :
            # Socket is broken
            socket.close()
            # Remove broken socket
            if socket in connections:
                connections.remove(socket)


if __name__ == "__main__":
    sys.exit(chat_server())
