import json
import os
import random
import socket
import threading
from messages import CommitRequestMessage, CommitResponseMessage, ReadRequestMessage
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
      self.pedding_commit = []
    
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
        data = self.recv_tcp(socket)
        socket.close()
        return data
      
      # Resposta da commit (Aceitação ou Abort)
      if protocol == sh.ProtocolType.UDP:
        try:
          # Tenta receber dados (não-bloqueante)
          data, _ = self.recv_udp(socket)
          socket.close()
          return data
        except BlockingIOError:
            # Não há dados disponíveis no momento
            self.pedding_commit.append(socket)
            return None

        # data = self.recv_udp(socket)
        # socket.close()
        # return data
    
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
            m = ReadRequestMessage(op.item, self.cid)
            socket = self.send(m)
            data   = self.recv(socket, sh.ProtocolType.TCP)
            self.rs[op.item] = data
        
        # Se é um operação de COMMIT, precisamos fazer uma difusão atômica
        elif op.type == OperationType.COMMIT:
          m = CommitRequestMessage(self.cid, int(self.transaction.id), self.rs, self.ws)
          socket = self.send(m)
          data  = self.recv(socket, sh.ProtocolType.UDP)
          if data is not None:
            if self.transaction.result != OperationType.ABORT.value:
              self.ws = {}
              self.rs = {}

        else: 
          self.transaction.result = OperationType.ABORT
        
        print("")

    def show_late_delivered(self):
      while True:
        lista = self.pedding_commit

        if not lista:
            return False

        for p in lista[:]:
            try:
              raw, _ = self.recv_udp(p)
              data = CommitResponseMessage.from_json(raw)
            except BlockingIOError:
              data = None

            if data is not None:
                print(f"Cliente {self.cid} recebeu confirmação para a transação {data.tid}")
                lista.remove(p)

            if len(lista) <= 0:
                return False

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

