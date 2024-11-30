import json
import socket
import threading

from config import Config
from messages import CommitRequestMessage


class Sequencer():
  def __init__(self, host, udp_port, servers):
    super().__init__()
    self.host = host
    self.udp_port = udp_port
    self.seq_number = 1

    # Criando sockets TCP e UDP
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind nos sockets
    self.udp_socket.bind((self.host, self.udp_port))

    self.servers = servers

  def handle_message(self, m, addr):
    m.seq = self.seq_number
    m.origin = addr
    
    for ipport in self.servers.values():
      host = ipport["HOST"]
      port = ipport["UDPPORT"]
      self.udp_socket.sendto(m.to_json().encode(), (host, port))
      print(f"send[de={addr[1]}; para={port}, t.id={m.tid}, seq={self.seq_number}]")
    self.seq_number += 1


  def handle_udp(self):
    while True:
      data, addr = self.udp_socket.recvfrom(1024)
      print(f"sequenciador addr do cliente {addr}")
      m = CommitRequestMessage.from_json(data.decode())
      self.handle_message(m, addr)

  def start(self):
    # Criando threads para TCP e UDP
    udp_thread = threading.Thread(target=self.handle_udp)

    # Iniciando as threads
    udp_thread.start()

    # Aguardando o término das threads (opcional)
    udp_thread.join()

# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  config = Config()
  sequencers = [Sequencer(config.sequencer[f"SEQUENCER{i}"]["HOST"], config.sequencer[f"SEQUENCER{i}"]["UDPPORT"], config.servers) for i in range(1)]

  for s in sequencers:
    s.start()
  # s1.execute()