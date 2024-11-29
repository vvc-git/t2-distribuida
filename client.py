import json
import os
import random
import socket
import threading
import socket_handler as sh
import testes as t
from config import Config
from transaction import *

class Client(sh.SocketHandler):
    def __init__(self, config, servers, sequencer):
      super().__init__(config['HOST'], config['TCPPORT'], config['UDPPORT'])
      self.cid = config['ID']
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
    
    def send(self, protocol, message):
      # TCP para leituras 
      if protocol == sh.ProtocolType.TCP:
        # Message deve vir pronta.
        # m = {"type": OperationType.READ.value, "item": item, "cid": self.cid}
        server = self.servers["SERVER" + str(random.randint(0, len(self.servers)- 1))]
        host   = server['HOST']
        port   = server['TCPPORT']

        # Cria o socket e conecta ao servidor
        socket = self.create(sh.ProtocolType.TCP)
        socket.connect((host, port))

        # É bloqueante. Espera até que todos os dados sejam enviados.
        print(f"send[={OperationType.READ.value}; de={socket.getsockname()[1]}; para={port}]")
        socket.sendall(json.dumps(message).encode())

        # Retorna o socket para o recv
        return socket
      
      elif protocol == sh.ProtocolType.UDP:
        sequencer = self.sequencer["SEQUENCER" + str(random.randint(0, len(self.sequencer)- 1))]
        host   = sequencer['HOST']
        port   = sequencer['TCPPORT']

        # Cria o socket e conecta ao servidor
        socket = self.create(sh.ProtocolType.UDP)

        socket.sendto(json.dumps(message).encode(), (host, port))
        print(f"send[={message['type']}; de={socket.getsockname()[1]}; para={port}, t.id={message['transaction_id']}]")

        return socket
         
    def recv(self, socket, protocol):
      if protocol == sh.ProtocolType.TCP:  
        data = json.loads(socket.recv(1024).decode())
        print(f"recv[={OperationType.READ.value}; de={socket.getsockname()[1]}; para={self.tcp_port}]")
        socket.close()
        return data
      if protocol == sh.ProtocolType.UDP:  
        data, addr = socket.recvfrom(1024)  # O segundo valor é o endereço do remetente
        response = json.loads(data.decode())
        print(f"recv[={response['type']}, de={addr[1]}, para={socket.getsockname()[1]}]")
        socket.close()
        return response

    # def read_from_sever(self, item):
    #   m = {"type": OperationType.READ.value, "item": item, "cid": self.cid}
    #   # Cria o socket (IPv4, TCP)
    #   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          
    #       s.bind((self.host, self.tcp_port))
          
    #       server = self.servers["SERVER" + str(random.randint(0, len(self.servers)- 1))]
    #       host   = server['HOST']
    #       port   = server['TCPPORT']
          
    #       # Conecta ao servidor
    #       s.connect((host, port))
          
    #       # É bloqueante. Espera até que todos os dados sejam enviados.
    #       print(f"send[={OperationType.READ.value}; de={s.getsockname()}; para={port}]")
    #       s.sendall(json.dumps(m).encode())
          
          
    #       # Recebe a resposta
    #       data = json.loads(s.recv(1024).decode())
    #       print(f"recv[={OperationType.READ.value}; de={port}; para={self.tcp_port}]")
    #       return data
      
    # def commit_to_sever(self, transaction_id):
    #   m = {"type": OperationType.COMMIT.value, "cid": self.cid, "transaction_id": int(transaction_id),"rs": self.rs, "ws": self.ws}
    #   # Cria o socket (IPv4, TCP)
    #   with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
          
    #       s.bind((self.host, self.udp_port))

    #       server = self.sequencer["SEQUENCER" + str(random.randint(0, len(self.sequencer)- 1))]
    #       host   = server['HOST']
    #       port   = server['UDPPORT']


    #       # Envia os dados ao sequenciador
    #       s.sendto(json.dumps(m).encode(), (host, port))
    #       print(f"send[={m['type']}; de={s.getsockname()[1]}; para={port}, t.id={m['transaction_id']}]")
          
    #       # Recebe a resposta do servidor
    #       data, addr = s.recvfrom(1024)  # O segundo valor é o endereço do remetente
    #       response = json.loads(data.decode())
    #       print(f"recv[={response['type']}, de={addr[1]}, para={s.getsockname()[1]}]")
    #       return response

    
    def execute(self):
      for op in self.transaction.operations:
          # Se é um operação de Escrita, então salva em ws
          if op.type == OperationType.WRITE:
            self.ws[op.item] = op.value
          
          # Se é um operação de Leitura, então verifica se já foi alterado localmente.
          elif op.type == OperationType.READ:
            # Se foi alterado localmente, então pega esse valor local.
            if op.item in self.ws:
              # A principio, não precisamos fazer nada. A transação usaria já o valor mais recente.
              print("Leu localmente")
              pass
            # Se NÃO foi alterado localmente, então SOLICITA do servidor.
            else:
              m = {"type": OperationType.READ.value, "item": op.item, "cid": self.cid}
              # data = self.read_from_sever(op.item)
              socket = self.send(sh.ProtocolType.TCP, m)
              data   = self.recv(socket, sh.ProtocolType.TCP)
              self.rs[op.item] = data
          
          # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
          elif op.type == OperationType.COMMIT:
            m = {"type": OperationType.COMMIT.value, "cid": self.cid, "transaction_id": int(self.transaction.id) ,"rs": self.rs, "ws": self.ws}
            socket = self.send(sh.ProtocolType.UDP, m)
            data   = self.recv(socket, sh.ProtocolType.UDP)
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
        thread = threading.Thread(target=getattr(t, f"teste3client{i}"), args=(clientes[i],))
        threads.append(thread)

    # Inicia as threads
    for thread in threads:
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()

