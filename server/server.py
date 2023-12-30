import socket
import threading
import os


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
        self.user_addresses.append((client_socket, username))

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                if message.startswith("/"):
                    self.handle_command(message, client_socket, username)
                else:
                    if message.startswith("@"):
                        self.send_private_message(message, username)
                    elif message.startswith("/file"):
                        self.receive_file(client_socket, username)
                    else:
                        self.broadcast(f"{username}: {message}", client_socket)

            except socket.error:
                break

        self.broadcast(f"{username} has left the chat", client_socket)
        self.clients.remove(client_socket)
        self.user_addresses = [(sock, uname) for sock, uname in self.user_addresses if sock != client_socket]
        client_socket.close()
        print(f"Connection from {client_address} closed")

    def broadcast(self, message, sender_socket):
        for client, username in self.user_addresses:
            if client != sender_socket:
                try:
                    client.sendall(message.encode('utf-8'))
                except socket.error:
                    # Handle a disconnected client if needed
                    pass

    def handle_command(self, command, sender_socket, username):
        if command.startswith("/list"):
            online_users = ", ".join(self.get_online_users())
            sender_socket.sendall(f"Online users: {online_users}".encode('utf-8'))
        elif command.startswith("/quit"):
            sender_socket.sendall("You are disconnecting...".encode('utf-8'))
            sender_socket.close()
        elif command.startswith("/login"):
            new_username = command.split()[1]
            if self.is_username_available(new_username):
                self.change_username(sender_socket, new_username)
            else:
                sender_socket.sendall("Username is already taken. Choose a different one.".encode('utf-8'))
        else:
            sender_socket.sendall("Unknown command. Type '/list' to see online users.".encode('utf-8'))

    def is_username_available(self, username):
        return username not in [existing_username for (_, existing_username) in self.user_addresses]

    def change_username(self, sender_socket, new_username):
        for i, (client, username) in enumerate(self.user_addresses):
            if client == sender_socket:
                self.user_addresses[i] = (client, new_username)
                sender_socket.sendall(f"Username changed to {new_username}".encode('utf-8'))
                break

    def send_private_message(self, message, sender_username):
        recipient_username, content = message.split(" ", 1)
        for client, username in self.user_addresses:
            if username == recipient_username:
                try:
                    client.sendall(f"(Private from {sender_username}) {content}".encode('utf-8'))
                    break
                except socket.error:
                    # Handle a disconnected client if needed
                    pass
        else:
            sender_socket = next(sock for sock, uname in self.user_addresses if uname == sender_username)
            sender_socket.sendall(f"User {recipient_username} not found or offline.".encode('utf-8'))

    def receive_file(self, sender_socket, sender_username):
        try:
            filename = sender_socket.recv(1024).decode('utf-8')
            file_content = sender_socket.recv(1024)

            if self.is_valid_filename(filename):
                self.broadcast_file(sender_socket, sender_username, filename, file_content)
            else:
                sender_socket.sendall("Invalid filename. File transfer aborted.".encode('utf-8'))

        except socket.error:
            print(f"Error receiving file from {sender_username}.")

    def broadcast_file(self, sender_socket, sender_username, filename, file_content):
        for client, username in self.user_addresses:
            if client != sender_socket:
                try:
                    client.sendall(f"(File from {sender_username}) {filename}".encode('utf-8'))
                    client.sendall(file_content)
                except socket.error:
                    # Handle a disconnected client if needed
                    pass

    def is_valid_filename(self, filename):
        # Check if the filename is valid (you can customize this validation)
        return filename.strip() != "" and not os.path.isfile(filename)

    def get_online_users(self):
        return [username for (_, username) in self.user_addresses]


if __name__ == "__main__":
    server = ChatServer('192.168.0.113', 8888)
    server.start()
