from enum import Enum
import socket as s

class ProtocolType(Enum):
   TCP = "TCP"
   UDP = "UDP"

class SocketHandler:
    def __init__(self, host, tcp, udp):
        self.host = host
        self.tcp_port = tcp
        self.udp_port = udp

    def create(self, protocol):
      if protocol == ProtocolType.TCP:
        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        socket.bind((self.host, self.tcp_port))
        return socket
      elif protocol == ProtocolType.UDP:
        socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        socket.bind((self.host, self.udp_port))
        return socket


    def send(self, protocol, message, dest_ip, dest_port):
      """
      Envia uma mensagem para o destino (aplicável tanto para TCP quanto UDP).
      Este método pode ser sobrescrito nas subclasses para comportamentos específicos.
      """
      raise NotImplementedError("Método send_message deve ser implementado na classe filha")
    
    def recv(self):
      """
      Envia uma mensagem para o destino (aplicável tanto para TCP quanto UDP).
      Este método pode ser sobrescrito nas subclasses para comportamentos específicos.
      """
      raise NotImplementedError("Método receive_message deve ser implementado na classe filha")


    def start_listening(self, buffer_size=1024):
      """
      Este método pode ser sobrescrito nas subclasses para lidar com conexões e mensagens.
      """
      raise NotImplementedError("Método start_listening deve ser implementado na classe filha")
  