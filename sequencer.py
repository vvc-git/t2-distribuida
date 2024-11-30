import json
import socket
import threading

from config import Config
from messages import CommitRequestMessage
from socket_handler import ProtocolType, SocketHandler


class Sequencer(SocketHandler):
  def __init__(self, host, port, servers):
    super().__init__(host=host, udp=port)
    self.socket = self.create(ProtocolType.UDP)
    self.socket.bind((self.host, self.udp_port))
    self.servers = servers
    self.seq_number = 1

  def _add_seq_origin(self, m, addr):
    # Adiciona o numero de sequencia e a origem do cliente para resposta ser direta
    m = CommitRequestMessage.from_json(m)
    m.seq = self.seq_number
    m.origin = addr
    
    return m

  def _foward_to_servers(self, m):
    # Reencaminha para todos os servidores.
    for ipport in self.servers.values():
      host = ipport["HOST"]
      port = ipport["UDPPORT"]
      self.send_udp(m, host, port, self.socket)
    self.seq_number += 1


  def run(self):
    print(f"Servidor Sequenciador escutando em: {self.host}:{self.udp_port}")
    while True:
      m_raw, addr = self.recv_udp(self.socket)
      m = self._add_seq_origin(m_raw, addr)
      self._foward_to_servers(m)

  def start(self):
    # Criando threads para TCP e UDP
    thread = threading.Thread(target=self.run)

    # Iniciando as threads
    thread.start()

    # Aguardando o término das threads (opcional)
    thread.join()

# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  config = Config()
  sequencers = [Sequencer(config.sequencer[f"SEQUENCER{i}"]["HOST"], config.sequencer[f"SEQUENCER{i}"]["UDPPORT"], config.servers) for i in range(1)]

  for s in sequencers:
    s.start()