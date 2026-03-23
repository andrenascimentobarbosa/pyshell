This project implements a minimal command-and-control (C2) architecture.
server.py listens for incoming connections, and once client.py connects, it establishes an interactive remote shell. Commands are sent over the socket, executed via subprocess on the client, and results are returned. Basic file transfer (upload/download) and directory navigation are supported.
