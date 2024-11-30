import json
import socket
import threading
import testes as t
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
    self.seq_number += 1
    
    return m

  def _foward_to_servers(self, m):
    # Reencaminha para todos os servidores.
    for ipport in self.servers.values():
      host = ipport["HOST"]
      port = ipport["UDPPORT"]
      self.send_udp(m, host, port, self.socket)
    

# Executa o servidor
if __name__ == "__main__":

  # Seta os IP e Portas 
  config = Config()

  # Lista de clientes - aqui você pode configurar a quantidade de clientes
  sequencers = [Sequencer(config.sequencer[f"SEQUENCER{i}"]["HOST"], config.sequencer[f"SEQUENCER{i}"]["UDPPORT"], config.servers) for i in range(1)]

  # Lista para armazenar as threads
  threads = []

  # Cria as threads para cada cliente
  for i in range(0, len(sequencers)):
      thread = threading.Thread(target=getattr(t, f"teste3sequencer{i}"), args=(sequencers[i],))
      threads.append(thread)

  # Inicia as threads
  for thread in threads:
      thread.start()

  # Aguarda todas as threads terminarem
  for thread in threads:
      thread.join()