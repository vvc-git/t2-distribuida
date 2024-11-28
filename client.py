from asyncio import sleep
import json
import os
import random
import socket
import threading
from config import Config
from testes import teste1, teste2
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
      self.udp_port_seq = 4000


    def read_from_sever(self, item):
      m = {"type": "read", "item": item, "cid": self.cid}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          # Conecta ao servidor
          s.connect((self.host, self.tcp_port))
          # É bloqueante = espera até que todos os dados sejam enviados. 
          s.sendall(json.dumps(m).encode())
          print(f"request[=read; de=; para={self.tcp_port}]")
          # Recebe a resposta
          data = json.loads(s.recv(1024).decode())
          print(f"response[=read; de={self.tcp_port}; para=]")
          return data
      
    def commit_to_sever(self, transaction_id):
      m = {"type": "commit", "cid": self.cid, "transaction_id": int(transaction_id),"rs": self.rs, "ws": self.ws}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
          # Envia os dados ao sequenciador
          s.sendto(json.dumps(m).encode(), (self.host, self.udp_port_seq))
          print("request[=abcast]")
          
          # Recebe a resposta do servidor
          data, addr = s.recvfrom(1024)  # O segundo valor é o endereço do remetente
          response = json.loads(data.decode())
          print(f"response[={response['type']}, de={addr[1]}]")
          return response

    
    def execute(self):
      for op in self.transaction.operations:
          # Se é um operação de Escrita, então salva em ws
          if op.get_type() == OperationType.WRITE:
            self.ws[op.get_item()] = op.get_value()
            print("Operação[=WRITE]")
          
          # Se é um operação de Leitura, então verifica se já foi alterado localmente.
          elif op.get_type() == OperationType.READ:
            print("Operação[=READ]")
            # Se foi alterado localmente, então pega esse valor local.
            if op.get_item() in self.ws:
              # A principio, não precisamos fazer nada. A transação usaria já o valor mais recente.
              pass
            # Se NÃO foi alterado localmente, então SOLICITA do servidor.
            else:
              data = self.read_from_sever(op.get_item())
              self.rs[op.get_item()] = data
          
          # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
          elif op.get_type() == OperationType.COMMIT:
            self.transaction.result = self.commit_to_sever(self.transaction.id)
          

          else: 
            self.result = OperationType.ABORT
      return False

def main():

    t1, t2 = teste1()

    # Seta os IP e Portas 
    config = Config()

    c1 = Client(config.clients["CLIENT1"], t1, config.servers)
    c2 = Client(config.clients["CLIENT2"], t2, config.servers)

    # Cria threads para executar transações concorrentes
    thread1 = threading.Thread(target=c1.execute)
    thread2 = threading.Thread(target=c2.execute)

    # Inicia as threads
    thread1.start()
    thread2.start()

    # Aguarda as threads terminarem
    thread1.join()
    thread2.join()



if __name__ == "__main__":
    main()

