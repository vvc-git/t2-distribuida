import json
import os
import random
import socket
import threading
from messages import CommitRequestMessage, ReadRequestMessage
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
    
    def send(self, message):
      # TCP para leituras no banco
      if isinstance(message, ReadRequestMessage):
        # Escolha aleatória do Servidor.
        server = self.servers["SERVER" + str(random.randint(0, len(self.servers)- 1))]
        host   = server['HOST']
        port   = server['TCPPORT']
    
        # Retorna o socket para o recv
        return self.send_tcp(message, host, port)
      
      # UDP para commits de transações
      elif isinstance(message, CommitRequestMessage):
        # Escolha aleatória do Sequenciador (Se tiver mais de um).
        sequencer = self.sequencer["SEQUENCER" + str(random.randint(0, len(self.sequencer)- 1))]
        host   = sequencer['HOST']
        port   = sequencer['TCPPORT']

        # Retorna o socket para o recv
        return self.send_udp(message, host, port)
         
    def recv(self, socket, protocol):
      # Resposta da leitura do banco
      if protocol == sh.ProtocolType.TCP:  
        return self.recv_tcp(socket)
      
      # Resposta da commit (Aceitação ou Abort)
      if protocol == sh.ProtocolType.UDP:  
        return self.recv_udp(socket)
    
    def execute(self):
      for op in self.transaction.operations:
        print(f"--------------------- {op.type.value} --------------------")

        # Se é um operação de Escrita, então salva em ws
        if op.type == OperationType.WRITE:
          self.ws[op.item] = op.value
          print(f"Escrita em ws[{op.item}]={self.ws[op.item]}")
        
        # Se é um operação de Leitura, então verifica se já foi alterado localmente.
        elif op.type == OperationType.READ:
          # Se foi alterado localmente, então pega esse valor local.
          if op.item in self.ws:
            # A principio, não precisamos fazer nada. A transação usaria já o valor mais recente.
            print(f"Leitura em ws[{op.item}]={self.ws[op.item]}")
            pass
          # Se NÃO foi alterado localmente, então SOLICITA do servidor.
          else:
            # m = {"type": OperationType.READ.value, "item": op.item, "cid": self.cid}
            m = ReadRequestMessage(op.item, self.cid)
            socket = self.send(m)
            data   = self.recv(socket, sh.ProtocolType.TCP)
            self.rs[op.item] = data
        
        # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
        elif op.type == OperationType.COMMIT:
          # m = {"type": OperationType.COMMIT.value, "cid": self.cid, "transaction_id": int(self.transaction.id) ,"rs": self.rs, "ws": self.ws}
          m = CommitRequestMessage(self.cid, int(self.transaction.id), self.rs, self.ws)
          socket = self.send(m)
          data   = self.recv(socket, sh.ProtocolType.UDP)
          if self.transaction.result != OperationType.ABORT.value:
            self.ws = {}
            self.rs = {}

        
        else: 
          self.transaction.result = OperationType.ABORT
        
        print("")

def main():

    # Seta os IP e Portas 
    config = Config()

    # Lista de clientes - aqui você pode configurar a quantidade de clientes
    clientes = [Client(config.clients[f"CLIENT{i}"], config.servers, config.sequencer) for i in range(1)]

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

