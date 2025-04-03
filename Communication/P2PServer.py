import socket
#GS

# Setup the server to listen for incoming connections
def p2p_server(host='10.33.138.229', port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            break
        print(f"Received: {data}")
        # Echo the message back
        conn.sendall(f"Echo: {data}".encode('utf-8'))

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    p2p_server()
