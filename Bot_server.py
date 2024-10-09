import socket
import os

# Function to get the server's IP address dynamically
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't send any data. It's just used to determine the local IP address.
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = '127.0.0.1'  # Fallback to localhost in case of failure
    finally:
        s.close()
    return ip

# Function to handle client requests
def handle_client(conn, addr):
    print(f"Connected by {addr}")

    try:
        data = conn.recv(1024).decode()

        if data.startswith('LIST'):
            # Handle file listing request
            files = os.listdir('.')  # List files in the current directory
            file_list = '\n'.join(files) if files else 'No files available.'
            conn.sendall(file_list.encode())

        elif data.startswith('DOWNLOAD'):
            # Handle file download request
            filename = data.split(' ')[1]
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    file_data = f.read()
                    conn.sendall(file_data)
                print(f"File '{filename}' sent to {addr}.")
            else:
                conn.sendall(b'ERROR: File not found.')

        elif data.startswith('UPLOAD'):
            # Handle file upload request
            filename = data.split(' ')[1]
            file_size = int(data.split(' ')[2])
            with open(filename, 'wb') as f:
                received = conn.recv(file_size)
                f.write(received)
            print(f"File '{filename}' uploaded successfully from {addr}.")
            conn.sendall(b'File uploaded successfully.')

        else:
            conn.sendall(b'Invalid command.')

    except Exception as e:
        print(f"Error while handling request: {e}")
        conn.sendall(f'ERROR: {str(e)}'.encode())
    
    finally:
        conn.close()

# Main function to start the server
def start_server(port=8080):
    ip = get_ip_address()
    print(f"Server is starting on {ip}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        print(f"Server listening on {ip}:{port}")

        while True:
            conn, addr = s.accept()  # Accept a connection from the client
            handle_client(conn, addr)  # Handle the client request

if __name__ == "__main__":
    start_server()
