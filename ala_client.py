import sys, socket, select, string

class color:
    PURPLE = '\033[35m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def ala_client():

    if(len(sys.argv) < 3) :
        print('Usage : python ala_client.py hostname username channel(optional)')
        sys.exit()

    # Some ANSI/VT100 Terminal Control Escape Sequences
    CSI = '\x1b['
    CLEAR = CSI + '2J'

    HOST = sys.argv[1]
    PORT = 6667
    NICK = sys.argv[2]
    PASSWORD = "lolmatron"
    CHANNEL = sys.argv[3] if len(sys.argv) > 3 else 'default'
    text = ""

    # HELPER FUNCTION
    def check_keywords(s, data):
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
        elif data.find("/msg") == 0 and len(data.split()) > 2:
            msg = "PRIVMSG %s: %s" % (data.split()[1], " ".join(data.split()[2:]))
            s.sendall(msg)
            return True
        elif data.find("/me") == 0:
            msg = color.PURPLE + color.BOLD + NICK + " " + " ".join(data.split()[1:]) + color.END
            s.sendall(msg)
            return True
        elif data.find("/join") == 0 and len(data.split()) > 1:
            msg = "JOIN %s\r\n" % data.split()[1].strip()
            s.sendall(msg)
            return True
        else:
            return False

    # Create socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();

    # Find ip of host
    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        # Could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    print 'Connecting to ' + remote_ip + ' on port ' + str(PORT) + ' with username ' + NICK
    # Connect to remote server
    try:
        print CLEAR
        s.connect((remote_ip , PORT))
        s.sendall("NICK %s\r\n" % NICK)
        s.sendall("JOIN %s\r\n" % CHANNEL)

        # These 2 needed for actual IRC
        # s.sendall("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK))
        # s.sendall("PRIVMSG nickserv :identify %s %s\r\n" % (NICK, PASSWORD))

        print 'Connected to ' + remote_ip + ' on port ' + str(PORT) + ' with username ' + NICK
    except:
        print 'Failed to connect'
        sys.exit()

    print("type /help for instructions")

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
                    if text.find("PING") != -1 and len(text.split()) > 1:
                        s.sendall("PONG " + text.split()[1] + '\r\n')
                    else:
                        # Print out what we received
                        print text.strip()
            else:
                # It was from us the message came
                data = sys.stdin.readline()
                if not check_keywords(s, data.strip()):
                    s.sendall(data)
                    sys.stdout.flush()

if __name__ == "__main__":
    sys.exit(ala_client())
