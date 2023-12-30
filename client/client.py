import socket
import threading
import os


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

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                if message.startswith("(File from"):
                    self.receive_file(message)
                else:
                    print(message)
            except socket.error:
                break

    def receive_file(self, message):
        try:
            _, _, filename = message.partition("(File from ")
            filename = filename.rstrip(")")
            file_content = self.client_socket.recv(1024)

            with open(self.unique_filename(filename), 'wb') as file:
                while file_content:
                    file.write(file_content)
                    file_content = self.client_socket.recv(1024)

            print(f"File '{filename}' received successfully.")
        except socket.error:
            print(f"Error receiving file '{filename}'.")

    def send_messages(self):
        while True:
            try:
                message = input()
                if message.startswith("/file"):
                    self.send_file(message)
                else:
                    self.client_socket.sendall(message.encode('utf-8'))
            except socket.error:
                break

    def send_file(self, message):
        try:
            _, _, filename = message.partition("/file")
            filename = filename.strip()
            if self.is_valid_filename(filename):
                self.client_socket.sendall(f"/file {filename}".encode('utf-8'))

                with open(filename, 'rb') as file:
                    file_content = file.read()
                    self.client_socket.sendall(file_content)

                print(f"File '{filename}' sent successfully.")
            else:
                print("Invalid filename. File transfer aborted.")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except socket.error:
            print(f"Error sending file '{filename}'.")

    def is_valid_filename(self, filename):
        # Check if the filename is valid (you can customize this validation)
        return filename.strip() != "" and os.path.isfile(filename)

    def unique_filename(self, filename):
        # Ensure filename is unique by adding a suffix if necessary
        original_filename, file_extension = os.path.splitext(filename)
        counter = 1

        while os.path.isfile(filename):
            filename = f"{original_filename}_{counter}{file_extension}"
            counter += 1

        return filename


if __name__ == "__main__":
    client = ChatClient('192.168.0.113', 8888)
    client.connect()
