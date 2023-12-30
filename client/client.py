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

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(data.decode('utf-8'))
            except socket.error:
                break

    def send_messages(self):
        while True:
            try:
                message = input()
                self.client_socket.sendall(message.encode('utf-8'))
            except socket.error:
                break


if __name__ == "__main__":
    client = ChatClient('localhost', 8888)
    client.connect()
