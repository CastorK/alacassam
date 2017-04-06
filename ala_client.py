import sys, socket, select, string

def check_keywords(data):
    if data == '/quit':
        sys.stdout.write('Exiting!\n')
        sys.stdout.flush()
        sys.exit()
        return True
    elif data == '/help':
        helpmsg = 'Type "/quit" to exit the program\n'
        sys.stdout.write(helpmsg)
        sys.stdout.flush()
        return True

    else:
        return False

def ala_client():

    if(len(sys.argv) < 4) :
        print('Usage : python ala_client.py hostname port channel username')
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    NICK = sys.argv[3]
    PASSWORD = "lolmatron"
    CHANNEL = sys.argv[3]
    text = ""

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();
    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        # Could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    print 'Connecting to ' + remote_ip + ' on port ' + str(PORT) + ' with username ' + NICK

    # Connect to remote server
    try:
        s.connect((remote_ip , PORT))
        s.send("NICK %s\r\n" % NICK)
        s.send("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK))
        s.send("PRIVMSG nickserv :identify %s %s\r\n" % (NICK, PASSWORD))
        s.send("JOIN %s\n" % CHANNEL)
        print 'Connected'
    except:
        print 'Failed to connect'
        sys.exit()

    sys.stdout.write("type /help for instructions\n")
    sys.stdout.flush()

    while True:
        socket_list = [sys.stdin, s]
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            if sock == s:
                # We received a message from the server
                text = sock.recv(4096)
                if not text:
                    # Read Failed
                    print 'Lost connection to server'
                    sys.exit()
                else:
                    if text.find("PING") != -1:
                        s.send("PONG " + text.split()[1] + '\r\n')
                    else:
                        # Print out what we received
                        print(text.strip())
            else:
                # It was from us the message came
                data = sys.stdin.readline()
                if check_keywords(data.strip()):
                    pass
                else :
                    # if there wasnt a keyword just send the data
                    s.send(data)
                    sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(ala_client())
