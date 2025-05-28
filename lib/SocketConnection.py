import socket
import ssl
import time

class SocketConnection:
    def __init__(self):
        self.context = None
        self.data = None
        self.sock = None
        self.ssl_sock = None
        self.ssl_enable = False

    def connect(self, host, port, timeout):
        try:
            if port == 443:
                self.ssl_enable = True
                self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                self.sock = socket.create_connection((host, port), timeout)
                self.ssl_sock = self.context.wrap_socket(self.sock, server_hostname=host)
                self.ssl_sock.settimeout(timeout)
            else:
                self.sock = socket.create_connection((host, port), timeout)
            return self.sock
        except socket.error as msg:
            print(f'Socket Error → {msg}')
            self.sock = None
            return None

    def send_payload(self, payload):
        if self.ssl_enable and self.ssl_sock:
            self.ssl_sock.sendall(str(payload).encode())
        elif self.sock:
            self.sock.sendall(str(payload).encode())
        else:
            raise Exception("No socket available for sending payload")

    def receive_data(self, buffer_size=1024):
        try:
            if self.ssl_enable and self.ssl_sock:
                self.ssl_sock.settimeout(None)
                self.data = self.ssl_sock.recv(buffer_size)
            elif self.sock:
                self.sock.settimeout(None)
                self.data = self.sock.recv(buffer_size)
            else:
                self.data = b''
        except socket.timeout:
            print('Error: Socket timeout')
            self.data = b''
        return self.data

    @staticmethod
    def detect_hrs_vulnerability(start_time, timeout):
        if time.time() - start_time >= timeout:
            return True
        return False

    def close_connection(self):
        try:
            if self.ssl_enable and self.ssl_sock:
                self.ssl_sock.close()
                self.ssl_sock = None
            if self.sock:
                self.sock.close()
                self.sock = None
        except Exception:
            pass