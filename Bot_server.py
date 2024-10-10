import socket
import os
from flask import Flask, jsonify, render_template_string, send_from_directory
import re

def escape_markdown(text):
    """Escape MarkdownV2 special characters in the text."""
    return re.sub(r'([_.*[\]()~`>#+\-!=|{}])', r'\\\1', text)

# Initialize Flask app
app = Flask(__name__)

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

# Flask API route to list files in the server's directory as hyperlinks
@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir('.')  # List files in the current directory
        # Create Markdown formatted links for each file
        file_links = '\n'.join([f'[{escape_markdown(file)}](http://{get_ip_address()}:8080/api/download/{escape_markdown(file)})' for file in files])
        return f"Files available for download:\n{file_links}", 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route to handle file downloads
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(os.getcwd(), filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

# Function to handle client requests (keeping socket functionality)
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
            filename = data.split(' ')[1]  # Extract filename
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    conn.sendfile(f)
            else:
                conn.sendall(b'File not found.')

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    ip = get_ip_address()
    print(f"Server running on {ip}:8080")
    
    # Run the Flask server on the detected IP and port 8080
    app.run(host=ip, port=8080)
