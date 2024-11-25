import json
import os
import random
import socket
import threading
from config import Config
from transaction import *
from atomic_broadcast import AtomicBroadcast

class Client():
    def __init__(self, cid, transaction, servers):
      self.cid = cid
      self.transaction = transaction
      # Lista de servidores disponíveis
      self.servers = servers
      # Seleciona aleatoriamente um servidor
      self.selected_server = "SERVER" + str(random.randint(0, len(self.servers)- 1))
      # Conjuntos de leitura (rs) e escrita (ws)
      self.ws = {}  # Conjunto de escritas
      self.rs = {}  # Conjunto de leituras
      self.result = None
      
      # Do servidor (Hardcoded) => Fazer depois usando o selected server
      self.host = '127.0.0.1'
      self.tcp_port = 2000
      self.udp_port = 3000

      # Do sequenciador (Hardcoded) => Fazer depois usando o selected server
      self.udp_port_seq = 3001




    def read_from_sever(self, item):
      m = {"type": "read", "item": item, "cid": self.cid}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          # Conecta ao servidor
          s.connect((self.host, self.tcp_port))
          # É bloqueante = espera até que todos os dados sejam enviados. 
          s.sendall(json.dumps(m).encode())
          # Recebe a resposta
          data = json.loads(s.recv(1024).decode())
          return data
      
    def commit_to_sever(self):
      m = {"type": "commit", "rs": self.rs, "ws": self.ws}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
          # Envia os dados ao servidor
          s.sendto(json.dumps(m).encode(), (self.host, self.udp_port_seq))
          print("Mensagem COMMIT (UDP) enviada para o Sequenciador", self.host + ":" + str(self.udp_port))
          
          # Recebe a resposta do servidor
          data, _ = s.recvfrom(1024)  # O segundo valor é o endereço do remetente
          response = json.loads(data.decode())
          print("Resposta do servidor:", response)

    
    def execute(self):
      for op in self.transaction.operations:
          # Se é um operação de Escrita, então salva em ws
          if op.get_type() == OperationType.WRITE:
            self.ws[op.get_item()] = op.get_value()
          
          # Se é um operação de Leitura, então verifica se já foi alterado localmente.
          elif op.get_type() == OperationType.READ:
            # Se foi alterado localmente, então pega esse valor local.
            if op.get_item() in self.ws:
              # A principio, não precisamos fazer nada. A transação usaria já o valor mais recente.
              print("Achou localmente")
            # Se NÃO foi alterado localmente, então SOLICITA do servidor.
            else:
              data = self.read_from_sever(op.get_item())
              self.rs[op.get_item()] = data
          
          # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
          elif op.get_type() == OperationType.COMMIT:
            self.commit_to_sever()
          else: 
            self.result = OperationType.ABORT
      return False

def main():
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.WRITE, item="chave1", value="Teste2"),
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)

    # Seta os IP e Portas 
    config = Config()

    t = Client(config.clients["CLIENT1"], t1, config.servers)

    # Cria threads para executar transações concorrentes
    thread = threading.Thread(target=t.execute)

    # Inicia as threads
    thread.start()

    # Aguarda as threads terminarem
    thread.join()


if __name__ == "__main__":
    main()

