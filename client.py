import json
import os
import random
import socket
import threading
import testes.teste1 as t
from config import Config
from transaction import *

class Client():
    def __init__(self, config, servers, sequencer):
      self.cid = config['ID']
      self.host= config['HOST']
      self.tcp_port = config['TCPPORT']
      self.udp_port = config['UDPPORT']
      self.transaction = None
      self.servers = servers
      self.sequencer = sequencer
      self.ws = {}  # Conjunto de escritas
      self.rs = {}  # Conjunto de leituras
      self.result = None
    
    @property
    def transaction(self):
        return self._transaction

    @transaction.setter
    def transaction(self, value):
      self._transaction = value


    def read_from_sever(self, item):
      m = {"type": "read", "item": item, "cid": self.cid}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          
          s.bind((self.host, self.tcp_port))
          
          server = self.servers["SERVER" + str(random.randint(0, len(self.servers)- 1))]
          host   = server['HOST']
          port   = server['TCPPORT']
          
          # Conecta ao servidor
          s.connect((host, port))
          
          # É bloqueante. Espera até que todos os dados sejam enviados. 
          s.sendall(json.dumps(m).encode())
          print(f"send[=read; de={self.tcp_port}; para={port}]")
          
          # Recebe a resposta
          data = json.loads(s.recv(1024).decode())
          print(f"recv[=read; de={port}; para={self.tcp_port}]")
          return data
      
    def commit_to_sever(self, transaction_id):
      m = {"type": "commit", "cid": self.cid, "transaction_id": int(transaction_id),"rs": self.rs, "ws": self.ws}
      # Cria o socket (IPv4, TCP)
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
          
          server = self.sequencer["SEQUENCER" + str(random.randint(0, len(self.sequencer)- 1))]
          host   = server['HOST']
          port   = server['UDPPORT']


          # Envia os dados ao sequenciador
          s.sendto(json.dumps(m).encode(), (host, port))
          print(f"send[={m['type']}; de={self.udp_port}; para={port}, t.id={m['transaction_id']}]")
          
          # Recebe a resposta do servidor
          data, addr = s.recvfrom(1024)  # O segundo valor é o endereço do remetente
          response = json.loads(data.decode())
          print(f"recv[={response['type']}, de={addr[1]}, para={self.udp_port}]")
          return response

    
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
              print("Leu localmente")
              pass
            # Se NÃO foi alterado localmente, então SOLICITA do servidor.
            else:
              data = self.read_from_sever(op.get_item())
              print("Data recebida do server: ", data)
              self.rs[op.get_item()] = data
          
          # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
          elif op.get_type() == OperationType.COMMIT:
            self.transaction.result = self.commit_to_sever(self.transaction.id)  
            if self.transaction.result != OperationType.ABORT.value:
              self.ws = {}
              self.rs = {}

          else: 
            self.transaction.result = OperationType.ABORT

def main():

    # Seta os IP e Portas 
    config = Config()

    # Lista de clientes - aqui você pode configurar a quantidade de clientes
    clientes = [Client(config.clients[f"CLIENT{i}"], config.servers, config.sequencer) for i in range(2)]

    # Lista para armazenar as threads
    threads = []

    # Cria as threads para cada cliente
    for i in range(0, len(clientes)):
        thread = threading.Thread(target=getattr(t, f"teste1client{i}"), args=(clientes[i],))
        threads.append(thread)

    # Inicia as threads
    for thread in threads:
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()

