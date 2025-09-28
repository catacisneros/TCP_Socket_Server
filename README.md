TCP Socket Server

Project Members:
Isabel Ruiz
Cata Cisneros (6517771)
Pedro Remior (6390824)

Language: Python 3

Compiling instructions:

Compile the file in the terminal with
py myftp.py <Server_Name> OR python myftp.py <Server_Name>


Program Description:

After compiling the file with the given server as a command line argument, the program will retrieve
a username and password from the user. The client socket will then attempt to connect to the provided server.
If a correct username is provided, the server should return a 220 code, and should return a 230 if the
user is already logged in or a 331 if a password is needed. All commands, such as entering a password or
user name, or downloading a file, are encoded in unicode utf-8 and are submitted to the server in the format of:

[CODE] [COMMAND] [CRLF]
see: section 5.3 of https://www.rfc-editor.org/rfc/rfc959

After accessing the server, the user will be prompted to enter one of the following commands:

ls:
Sends a request to the server to return the name of all files and folders in the current directory

cd [Directory]:
Sends a request to move to the provided directory

get [File]
Sends a request to download a file from the server to the client

put [File]
Sends a request to submit a file from the local client to the server

delete [File]
Sends a request to delete a given file on the server

quit:
Ends the connection to the server by sending a quit command, then exits the program

The loop constantly requesting the user for commands will run until the connection ends or the user sends a quit command


Passive Mode:

This FTP server works in passive mode, as it is responsible and initiating both the client and data sockets.
When a command is given that requires transmitting file data (ls, get, put), the client sends a PASV command
to the server. The server then chooses a port for the client to connect to, the client than creates a data socket
and connects to the given port.

See: https://slacksite.com/other/ftp.html






