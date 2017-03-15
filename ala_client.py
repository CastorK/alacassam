import sys, socket, select

def check_keywords(data):
    if data == '!quit':
        sys.stdout.write('Exiting!\n')
        sys.stdout.flush()
        sys.exit()

def ala_client():

    if(len(sys.argv) < 4) :
        print('Usage : python ala_client.py hostname port username')
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    USERNAME = sys.argv[3]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();

    print "Socket Created!"

    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        # Could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    print 'Connecting to ' + remote_ip + ' on port ' + str(PORT) + ' with username ' + USERNAME

    # Connect to remote server
    try:
        s.connect((remote_ip , PORT))
        print 'Connected'
    except:
        print 'Failed to connect'
        sys.exit()

    sys.stdout.write('[%s] ' % USERNAME)
    sys.stdout.flush()

    while True:
        socket_list = [sys.stdin, s]
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            if sock == s:
                # We received a message from the server
                data = sock.recv(4096)
                if not data:
                    # Read Failed
                    print 'Lost connection to server'
                    sys.exit()
                else:
                    # Print out what we received
                    sys.stdout.write(data)
                    sys.stdout.write('[%s] ' % USERNAME)
                    sys.stdout.flush()
            else:
                # It was from us the message came
                data = sys.stdin.readline()
                check_keywords(data.strip())
                s.send(data)
                sys.stdout.write('[%s] ' % USERNAME)
                sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(ala_client())
