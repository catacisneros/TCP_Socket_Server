
# Help: https://www.eventhelix.com/networking/ftp/
# Help: https://www.eventhelix.com/networking/ftp/FTP_Port_21.pdf
# Help: https://realpython.com/python-sockets/
# Help: PASV mode may be easier in the long run. Active mode works 
# Reading: https://unix.stackexchange.com/questions/93566/ls-command-in-ftp-not-working
# Reading: https://stackoverflow.com/questions/14498331/what-should-be-the-ftp-response-to-pasv-command

#import socket module
from socket import *
import sys # In order to terminate the program

def quitFTP(clientSocket):
    command = "QUIT" + "\r\n"  # send QUIT with the required CRLF
    dataOut = command.encode("utf-8")
    clientSocket.sendall(dataOut)
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    print(data)

def sendCommand(socket, command):
    dataOut = command.encode("utf-8")
    socket.sendall(dataOut)  # push command on control channel
    dataIn = socket.recv(1024)  # grab reply from server
    data = dataIn.decode("utf-8")  # present reply as text
    return data



def receiveData(clientSocket):
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    return data

# If you use passive mode you may want to use this method but you have to complete it
# You will not be penalized if you don't
def modePASV(clientSocket):
    command = "PASV" + "\r\n"
    data = sendCommand(clientSocket, command)  # ask server to pick a passive port
    dataSocket = None  # fallback socket when PASV fails
    status = 0
    status = int(data[:3]) if data[:3].isdigit() else 0
    if status == 227:
        tupleSection = data[data.find("(") + 1:data.find(")")]  # grab the host/port tuple
        parts = tupleSection.split(",")  # split into numbers
        if len(parts) != 6:
            return 0, dataSocket
        ip = ".".join(parts[:4])  # rebuild dotted IP
        port = (int(parts[4]) << 8) + int(parts[5])  # combine the two port bytes
        dataSocket = socket(AF_INET, SOCK_STREAM)  # open data channel socket
        dataSocket.connect((ip, port))
    return status, dataSocket

    
    
def main():
    if len(sys.argv) < 2:  # need a server target
        print("Usage: python myftp.py <server-hostname>")  # quick hint for running
        sys.exit(1)

    username = input("Enter the username: ")
    password = input("Enter the password: ")

    clientSocket = socket(AF_INET, SOCK_STREAM) # TCP socket
    PORT = 21  # FTP control port

    HOST = sys.argv[1]  # server name or IP
    dataSocket = None  # placeholder for data link
    try:
        clientSocket.connect((HOST, PORT))  # open control channel
    except OSError as error:
        print(f"Failed to connect to {HOST}:{PORT} -> {error}")  # bubble up the socket error
        sys.exit(1)

    dataIn = receiveData(clientSocket)
    print(dataIn)

    status = 0
    
    if dataIn.startswith("220"):
        status = 220
        print("Sending username")
        userCommand = f"USER {username}\r\n"  # build USER command
        userResponse = sendCommand(clientSocket, userCommand)
        print(userResponse)

        if userResponse.startswith("230"):
            status = 230  # logged in already
        elif userResponse.startswith("331"):
            print("Sending password")
            passCommand = f"PASS {password}\r\n"  # send PASS next
            passResponse = sendCommand(clientSocket, passCommand)
            print(passResponse)
            if passResponse.startswith("230"):
                status = 230
                dataIn = passResponse
            else:
                print("Password rejected by server; closing connection.")
                quitFTP(clientSocket)
                clientSocket.close()
                sys.exit(1)
        else:
            print("Server rejected the supplied username; aborting session.")
            clientSocket.close()
            sys.exit(1)

       
    if status == 230:
        # It is your choice whether to use ACTIVE or PASV mode. In any event:
        print("Authentication complete. Available commands: ls, cd, get, put, delete, quit.")  # session ready message
        pasvStatus, dataSocket = modePASV(clientSocket)
        if pasvStatus == 227:
            if dataSocket is not None:  # drop the initial PASV socket
                dataSocket.close()
                dataSocket = None
            while True:  # command loop
                commandLine = input("myftp> ").strip()  # prompt user
                if not commandLine:  # skip blanks
                    continue
                tokens = commandLine.split()
                verb = tokens[0].lower()  # command keyword
                args = tokens[1:]  # rest of the words

                if verb == "quit":  # quit session
                    if dataSocket is not None:  # drop stray data channel
                        dataSocket.close()
                        dataSocket = None
                    quitFTP(clientSocket)
                    clientSocket.close()
                    print("Disconnecting...")
                    return

                elif verb == "ls":  # remote listing
                    pasvStatus, dataSocket = modePASV(clientSocket)  # new passive channel
                    if pasvStatus != 227:  # PASV failed
                        print("Failed to enter passive mode for ls.")
                        continue
                    response = sendCommand(clientSocket, "LIST\r\n")
                    print(response.strip())
                    if response.startswith(("125", "150")):
                        receivedChunks = []  # stash listing bytes
                        bytesTransferred = 0  # count bytes sent
                        while True:  # pull until server closes
                            chunk = dataSocket.recv(4096)
                            if not chunk:  # transfer done
                                break
                            bytesTransferred += len(chunk)
                            receivedChunks.append(chunk)
                        dataSocket.close()
                        dataSocket = None
                        listingText = b"".join(receivedChunks).decode("utf-8", errors="ignore")  # decode the directory listing
                        if listingText:
                            print(listingText, end="" if listingText.endswith("\n") else "\n")
                        finalResponse = receiveData(clientSocket)
                        print(finalResponse.strip())
                        print(f"Success: transferred {bytesTransferred} bytes.")
                    else:
                        dataSocket.close()
                        dataSocket = None

                elif verb == "cd":  # change remote dir
                    if not args:  # needs target
                        print("Usage: cd <remote-dir>")
                        continue
                    remoteDir = " ".join(args)  # keep spaces intact
                    response = sendCommand(clientSocket, f"CWD {remoteDir}\r\n")
                    print(response.strip())

                elif verb == "get":  # download a file
                    if not args:  # need filename
                        print("Usage: get <remote-file>")
                        continue
                    remoteFile = args[0]
                    pasvStatus, dataSocket = modePASV(clientSocket)  # passive link for download
                    if pasvStatus != 227:
                        print("Failed to enter passive mode for get.")
                        continue
                    response = sendCommand(clientSocket, f"RETR {remoteFile}\r\n")
                    print(response.strip())
                    if response.startswith(("125", "150")):
                        bytesTransferred = 0
                        downloadSucceeded = True
                        try:
                            with open(remoteFile, "wb") as localFile:
                                while True:
                                    chunk = dataSocket.recv(4096)
                                    if not chunk:
                                        break
                                    localFile.write(chunk)
                                    bytesTransferred += len(chunk)
                        except OSError as error:
                            downloadSucceeded = False
                            print(f"Unable to write local file '{remoteFile}': {error}")
                        dataSocket.close()
                        dataSocket = None
                        finalResponse = receiveData(clientSocket)
                        print(finalResponse.strip())
                        if downloadSucceeded:
                            print(f"Success: downloaded {bytesTransferred} bytes.")
                    else:
                        dataSocket.close()
                        dataSocket = None

                elif verb == "put":  # upload a file
                    if not args:  # need local file
                        print("Usage: put <local-file>")
                        continue
                    localFileName = args[0]
                    try:
                        localFile = open(localFileName, "rb")  # read source file
                    except OSError as error:
                        print(f"Unable to open local file '{localFileName}': {error}")
                        continue
                    pasvStatus, dataSocket = modePASV(clientSocket)  # passive link for upload
                    if pasvStatus != 227:
                        print("Failed to enter passive mode for put.")
                        localFile.close()
                        continue
                    response = sendCommand(clientSocket, f"STOR {localFileName}\r\n")
                    print(response.strip())
                    bytesTransferred = 0
                    uploadAccepted = response.startswith(("125", "150"))
                    if uploadAccepted:
                        while True:
                            chunk = localFile.read(4096)
                            if not chunk:
                                break
                            dataSocket.sendall(chunk)
                            bytesTransferred += len(chunk)
                    else:
                        print("Server declined the STOR request.")
                    localFile.close()
                    dataSocket.close()
                    dataSocket = None
                    if uploadAccepted:
                        finalResponse = receiveData(clientSocket)
                        print(finalResponse.strip())
                        print(f"Success: uploaded {bytesTransferred} bytes.")

                elif verb == "delete":  # remove remote file
                    if not args:  # needs target file
                        print("Usage: delete <remote-file>")
                        continue
                    remoteTarget = " ".join(args)  # keep spacing
                    response = sendCommand(clientSocket, f"DELE {remoteTarget}\r\n")
                    print(response.strip())

                else:
                    print("Unrecognized command. Available: ls, cd, get, put, delete, quit.")


    print("Disconnecting...")
    

    clientSocket.close()
    if dataSocket is not None:
        dataSocket.close()
    
    sys.exit()  # end program

main()
