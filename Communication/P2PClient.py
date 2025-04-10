import socket
#AGV

# Setup the client to connect to the server
def p2p_client(server_ip, port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    print(f"Connected to server at {server_ip}:{port}")

    try:
        while True:
            message = input("Enter message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            client_socket.sendall(message.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Received from server: {response}")
    except KeyboardInterrupt:
        print("\nClient disconnected")
    finally:
        client_socket.close()

if __name__ == "__main__":
    server_ip = '10.33.253.71'
    p2p_client(server_ip)
