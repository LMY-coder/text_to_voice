import socket
import time
import threading


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class server:

    def __init__(self, ip, host):
        self.ip = ip
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((ip, host))
        self.s.listen(1)
        self.msg = ''
        self.flag = False

    def receive(self):

        print(f"waiting for handshake at {self.ip}:{self.host}")
        self.conn, self.addr = self.s.accept()
        print(f"shake hand at {self.ip}:{self.host} success")
        while True:
            try:
                data = b''
                length_bytes = self.conn.recv(4)
                length = int.from_bytes(length_bytes, 'little')

                while len(data) < length:
                    data += self.conn.recv(1024)

                msg = data.decode()
                if (msg != ""):
                    self.msg = msg
                    print(
                        f"receive from {self.addr} : length={length} msg={self.msg}")
                    self.flag = True
                    self.conn.close()

            except:
                print(f"{self.ip}:{self.host} waiting for reconnect!\n", end="")
                time.sleep(1)
                self.conn, self.addr = self.s.accept()

    def start(self):
        t = threading.Thread(target=self.receive)
        t.start()

    def get_msg(self):
        return self.msg


if __name__ == "__main__":
    ip = get_ip()
    host = 8080
    s = server(ip, host)
    s.start()
    # 192.168.167.179
