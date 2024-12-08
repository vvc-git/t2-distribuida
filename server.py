from time import sleep
from config import Config
from socket_handler import ProtocolType, SocketHandler
from transaction import *
import socket
import json
import threading
import sys
from messages import AbortResponseMessage, CommitRequestMessage, CommitResponseMessage, ReadRequestMessage, ReadResponseMessage


class Server(SocketHandler):
  def __init__(self, host, tcp_port, udp_port, servers):
    super().__init__(host=host, tcp=tcp_port, udp=udp_port)
    self.db = {"chave1": ("Teste", 0), "chave2": ("Teste", 0)}

    # Criando sockets TCP e UDP
    self.tcp_socket = self.create(ProtocolType.TCP)
    self.udp_socket = self.create(ProtocolType.UDP)

    # Bind nos sockets
    self.tcp_socket.bind((self.host, self.tcp_port))
    self.udp_socket.bind((self.host, self.udp_port))

    # Configurando o socket TCP para escutar conexões
    self.tcp_socket.listen(5)  # Máximo de 5 conexões pendentes

    self.received = []
    self.pending = []
    self.sequence_number = 1
    self.servers = servers

  # No TCP, recebe apenas leituras. 
  def handle_read(self):
    print(f"Servidor escutando requisições de LEITURA em {self.host}:{self.tcp_port}")
    while True:
      conn, addr = self.tcp_socket.accept()

      # Recebe uma requisição para leitura no bd
      data = conn.recv(1024).decode()
      m = ReadRequestMessage.from_json(data)
      print(f"send[=read; de={addr[1]}; para={self.tcp_port}]")

      # Responde com o valor do bd
      response = self.handle_message(m).to_json()
      conn.sendall(response.encode())
      print(f"recv[=read; de={self.tcp_port}; para={addr[1]}]")

      # Fecha a conexão
      conn.close()

  def handle_commit(self):
    print(f"Servidor escutando requisições de COMMIT em {self.host}:{self.udp_port}")
    while True:
        m_raw, addr = self.recv_udp(self.udp_socket)
        m = CommitRequestMessage.from_json(m_raw)
        
        if (self.deliver(m, addr)):
          h = self.handle_message(m)

          #  Respondendo diretamente para o cliente.
          self.send_udp(h, m.origin[0], m.origin[1], self.udp_socket)
        
        else:
          print(f"Servidor recebe fora de ordem: tid={m.tid} seq={m.seq}")
           


  def deliver(self, message, addr):

    if message not in self.received:
      self.received.append(message)

      for ipport in self.servers.values():
        host = ipport["HOST"]
        port = ipport["UDPPORT"]
        
        # Caso 1: Não envia para servidores que estão retransmitindo a mensagem (Eles já há tem)
        # Caso 2: Não envia para si mesmo para evitar loops
        if (int(addr[1]) != (port)) and (int(self.udp_port) != (port)):
          self.send_udp(message, host, port, self.udp_socket)
         

    # Se a mensagem for a próxima esperada, entregamos imediatamente
    if message.seq == self.sequence_number:
        print(f"deliverd[id={message.tid}, seq={message.seq}]")
        self.sequence_number += 1

        # Depois de entregar a mensagem, verificamos se há mais mensagens para entregar
        self._deliver_next()
        return True

    # Caso contrário, armazenamos a mensagem no buffer
    else:
        self.pending.append(message)
        return False

  def _deliver_next(self):
      # Verifica se a próxima mensagem está no buffer
      while (self.sequence_number) in [msg.seq for msg in self.pending]:
          # Encontra a próxima mensagem que pode ser entregue
          next_message = next(msg for msg in self.pending if msg.seq == self.sequence_number)

          # Remove a mensagem do buffer
          self.pending = [msg for msg in self.pending if msg.seq != self.sequence_number]  
          print(f"deliverd[id={next_message.tid}, seq={self.sequence_number}]")
          
          # Verifica se não tem leituras desatualizadas
          h = self.handle_message(next_message)

          #  Respondendo diretamente para o cliente.
          self.send_udp(h, next_message.origin[0], next_message.origin[1], self.udp_socket)

          self.sequence_number += 1


  def start(self):
      # Criando threads para TCP e UDP
      tcp_thread = threading.Thread(target=self.handle_read)
      udp_thread = threading.Thread(target=self.handle_commit)

      # Iniciando as threads
      tcp_thread.start()
      udp_thread.start()

      # Aguardando o término das threads (opcional)
      tcp_thread.join()
      udp_thread.join()

  def handle_message(self, m):

      # Se for leitura, pega do banco retorna e retorna para o cliente
      if isinstance(m, ReadRequestMessage):
        (value, version) = self.db[m.item]
        return ReadResponseMessage(value, version)
      
      # Se for commit, realiza algumas verificações
      else:
        # Para cada operação da transação,
        # Verifica se utilizou um valor antigo para suas manipulações.
        for item, value_version in m.rs.items():
          # Se utilizou um valor antigo, aborta.
          if self.db[item][1] > value_version['version']:
            return AbortResponseMessage(m.tid)
        
        # Se NÃO utilizou um valor antigo, atualiza o banco.
        for item, value in m.ws.items():
          version = self.db[item][1] + 1 
          update = value
          self.db[item] = (update, version)

        return CommitResponseMessage(m.tid)
          
# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  identificador = sys.argv[1]
  config = Config()
  host = config.servers["SERVER" + identificador]["HOST"]
  tcp_port = config.servers["SERVER" + identificador]["TCPPORT"]
  udp_port = config.servers["SERVER" + identificador]["UDPPORT"]

  s1 = Server(host, tcp_port, udp_port, config.servers)
  s1.start()



