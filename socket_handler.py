from enum import Enum
import json
import socket as s

from transaction import OperationType

class ProtocolType(Enum):
   TCP = "TCP"
   UDP = "UDP"

class SocketHandler:
    def __init__(self, host, tcp=None, udp=None):
        self.host = host
        self.tcp_port = tcp
        self.udp_port = udp

    def create(self, protocol):
      if protocol == ProtocolType.TCP:
        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        return socket
      elif protocol == ProtocolType.UDP:
        socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        return socket


    def send_tcp(self, message, host, port):
      # Cria o socket e conecta ao servidor
      socket = self.create(ProtocolType.TCP)
      socket.connect((host, port))

      # É bloqueante. Espera até que todos os dados sejam enviados.
      print(f"send[de={socket.getsockname()[1]}; para={port}]")
      socket.sendall(message.to_json().encode())

      return socket
    
    def send_udp(self, message, host, port, socket=None):
      # Cria o socket
      if not(socket):
        socket = self.create(ProtocolType.UDP)

      socket.sendto(message.to_json().encode(), (host, port))
      print(f"send[de={socket.getsockname()[1]}; para={port}, t.id={message.tid}]")

      return socket

    def recv_tcp(self, socket):
      data = json.loads(socket.recv(1024).decode())
      print(f"[de={socket.getsockname()[1]}; para={self.tcp_port}]")
      return data
    
    def recv_udp(self, socket):
      data, addr = socket.recvfrom(1024) 
      response   = data.decode()
      print(f"recv[de={addr[1]}, para={socket.getsockname()[1]}]")
      return response, addr