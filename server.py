import json
import socket
import threading
import time

import rumps

import prefs

# if we lose beacons from a host for this long, remove it from the list
HOST_TIMEOUT = 20


class Server:
    def __init__(
        self,
        port=prefs.DEFAULT_PORT,
        cb=lambda _: print("no callback"),
        sh=lambda _: print("no set hosts"),
        pw="insecure",
    ):
        self.port = int(port)
        self.cb = cb
        self.sh = sh
        self.pw = pw
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.settimeout(5)
        self.beacon_timer = rumps.Timer(lambda _: self.beacon(), 3)
        self.beacon_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.beacon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.status = [False]
        self.hosts = dict()

    def start(self):
        self.beacon_timer.start()
        self.server_socket.bind(("0.0.0.0", self.port))
        self.status[0] = True
        self.server_thread = threading.Thread(
            target=self.loop,
            args=(
                self.status,
                self.hosts,
            ),
        )
        self.server_thread.start()
        print("Server started")

    def loop(self, status, hosts):
        while True:
            if status[0] is False:
                break
            try:
                msg_raw, (ip, pt) = self.server_socket.recvfrom(256)
                try:
                    # TODO: decrypt the encoded payload using self.pw
                    msg = json.loads(msg_raw)
                except json.JSONDecodeError:
                    continue
                if msg["from"] == socket.gethostname():
                    continue
                if msg["to"] == "*":
                    hosts[msg["from"]] = time.time()
                    continue
                if msg["to"] == socket.gethostname():
                    threading.Thread(target=self.cb, args=(msg,)).start()
            except socket.timeout:
                pass

    def beacon(self):
        """sends a json message to the broadcast address"""
        for host in list(self.hosts):
            if time.time() - HOST_TIMEOUT > self.hosts[host]:
                self.hosts.pop(host)
        self.sh(self.hosts)
        self.send("*")

    def send(self, host: str):
        msg = json.dumps(
            {
                "from": socket.gethostname(),
                "to": host,
            }
        )
        # TODO: encrypt the encoded payload using self.pw
        self.beacon_socket.sendto(msg.encode(), ("255.255.255.255", self.port))

    def stop(self):
        self.beacon_timer.stop()
        self.status[0] = False
        self.server_thread.join()
        self.server_socket.close()
        print("Server stopped")
