import socket
import time


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # print(s.getsockname()[0])
    return s.getsockname()[0]


class client:

    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_server(self):
        while True:
            try:
                self.s.connect((self.ip, self.host))
                print(f"client connected to {self.ip}:{self.host}")
                break
            except:
                print(f"client waiting on {self.ip}:{self.host}")
                time.sleep(1)

    def is_connected(self):
        try:
            self.s.send(b'')
            return True

        except:
            return False

    def send_data(self, data):
        while True:
            try:
                length = len(data)
                self.s.send(length.to_bytes(4, 'big'))
                print(f"send data length '{length}' success")
                self.s.send(data.encode())
                print(f"send data '{data}' success")
                break
            except Exception as e:
                # print(e)
                self.connect_server()


if __name__ == "__main__":
    ip = get_ip()
    host = 8080
    c = client("192.168.167.179", host)
    # with open("test.txt", "r") as f:
    # data = f.read()
    data = "Wo shi Liu Shao"
    while True:
        c.send_data(data)
