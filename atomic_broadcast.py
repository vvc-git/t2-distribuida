import socket
import json

class AtomicBroadcast:
    def __init__(self):
        self.host = None
        self.port = None
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, cid, tid, rs, ws):
      """Primitiva 1:1 utilizando socket TCP (garantem entrega e ordem FIFO)"""
      pass

    def receive(self):
        """Primitiva 1:1 utilizando socket TCP (garantem entrega e ordem FIFO)"""
        pass
        
    def broadcast(self, m, servers):
      """Primitiva 1:n (garantem entrega e ordem TOTAL)"""
      pass
    def deliver(self):
      """Primitiva 1:n (garantem entrega e ordem TOTAL)"""
      pass
    