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
    # COMPLETE
    dataOut = command.encode("utf-8")
    clientSocket.sendall(dataOut)
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")

    print(data)

def sendCommand(socket, command):
    dataOut = command.encode("utf-8")
    data = socket.send(dataOut)

    return data



def receiveData(clientSocket):
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    return data

# If you use passive mode you may want to use this method but you have to complete it
# You will not be penalized if you don't
def modePASV(clientSocket):
    command = "PASV" + "\r\n"
    # Complete
    status = 0
    if data.startswith(""):
        status = 227
        # Complete
        dataSocket.connect((ip, port))
        
    return status, dataSocket

    
    
def main():
    # COMPLETE

    #Retrives server name from command line argument, otherwise from user input
    HOST = ""
    if(len(sys.argv) <= 1):
        HOST = input("Enter the server name: ")
    else:
        HOST = sys.argv[1:]

    username = input("Enter the username: ")
    password = input("Enter the password: ")

    clientSocket = socket(AF_INET, SOCK_STREAM) # TCP socket
    # COMPLETE

    #Connects to server through port 21 - control port
    clientSocket.connect((HOST, 21))

    #Print status code to user, valid connection results in a 220 code
    dataIn = receiveData(clientSocket)
    print(dataIn)

    status = 0
    
    if dataIn.startswith("220"):
        status = 220 #Server ready for new user
        print("Sending username")

        #FTP commands are in the structure of [Command Code] [Parameters] [Carriage return, line feed] 
        #See section 5.3 of https://datatracker.ietf.org/doc/html/rfc959#autoid-5

        command = "USER " + username + "\r\n"
        sendCommand(clientSocket, command)

        #Receive status code from server
        dataIn = receiveData(clientSocket)
        # COMPLETE
        
        print(dataIn)

        print("Sending password")

        #Only send password if status = 331 -> Username ok, password needed
        if dataIn.startswith("331"):
            status = 331
            command = "PASS " + password + "\r\n"
            sendCommand(clientSocket, command)

            #Ensure server received password
            dataIn = receiveData(clientSocket)

            # COMPLETE
            
            print(dataIn)
            if dataIn.startswith("230"):
                status = 230

       
    if status == 230:
        # It is your choice whether to use ACTIVE or PASV mode. In any event:
        # COMPLETE
        pasvStatus, dataSocket = modePASV(clientSocket)
        if pasvStatus == 227:
            # COMPLETE
            print("test")
    
    print("Disconnecting...")
    

    clientSocket.close()
    dataSocket.close()
    
    sys.exit()#Terminate the program after sending the corresponding data

main()

