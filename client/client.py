import socket
import threading


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        username_prompt = self.client_socket.recv(1024).decode('utf-8')
        print(username_prompt, end="")
        username = input()
        self.client_socket.sendall(username.encode('utf-8'))

        receive_thread = threading.Thread(target=self.receive_messages)
        send_thread = threading.Thread(target=self.send_messages)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

        self.client_socket.close()

    def send_messages(self):
        while True:
            try:
                message = input()
                self.client_socket.sendall(message.encode('utf-8'))
            except socket.error:
                break

    # Add the following method to ChatClient
    def send_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                file_content = file.read()
                self.client_socket.sendall(f"/file {filename}".encode('utf-8'))
                self.client_socket.sendall(file_content)
                print(f"File '{filename}' sent successfully.")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")

    # Modify the receive_messages method to handle incoming files
    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                if message.startswith("/file"):
                    filename = message.split()[1]
                    self.receive_file(filename)
                else:
                    print(message)
            except socket.error:
                break

    def receive_file(self, filename):
        try:
            file_content = self.client_socket.recv(1024)
            with open(filename, 'wb') as file:
                file.write(file_content)
                print(f"File '{filename}' received successfully.")
        except socket.error:
            print(f"Error receiving file '{filename}'.")


if __name__ == "__main__":
    client = ChatClient('localhost', 8888)
    client.connect()
