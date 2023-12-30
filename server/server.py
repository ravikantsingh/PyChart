import socket
import threading


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.user_addresses = []

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening for connections on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()
            self.clients.append(client_socket)

    def handle_client(self, client_socket, client_address):
        print(f"New connection from {client_address}")
        client_socket.sendall("Enter your username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        print(f"{client_address} chose username: {username}")
        self.broadcast(f"{username} has joined the chat", client_socket)

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                if message.startswith("/"):
                    self.handle_command(message, client_socket, username)
                else:
                    self.broadcast(f"{username}: {message}", client_socket)

            except socket.error:
                break

        self.broadcast(f"{username} has left the chat", client_socket)
        self.clients.remove(client_socket)
        client_socket.close()
        print(f"Connection from {client_address} closed")

    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode('utf-8'))
                except socket.error:
                    self.clients.remove(client)

    def handle_command(self, command, sender_socket, username):
        if command.startswith("/list"):
            online_users = ", ".join(self.get_online_users())
            sender_socket.sendall(f"Online users: {online_users}".encode('utf-8'))
        elif command.startswith("/quit"):
            sender_socket.sendall("You are disconnecting...".encode('utf-8'))
            sender_socket.close()
        else:
            sender_socket.sendall("Unknown command. Type '/list' to see online users.".encode('utf-8'))

    def get_online_users(self):
        return [username for (_, username) in self.user_addresses]


if __name__ == "__main__":
    server = ChatServer('localhost', 8888)
    server.start()
