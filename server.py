from time import sleep
from config import Config
from transaction import *
import socket
import json
import threading
import sys
from messages import AbortResponseMessage, CommitRequestMessage, CommitResponseMessage, ReadRequestMessage, ReadResponseMessage


class Server():
  def __init__(self, host, tcp_port, udp_port):
    super().__init__()
    self.last_commit = 0
    self.db = {"chave1": ("Teste", 0), "chave2": ("Teste", 0)}
    self.host = host
    self.tcp_port = tcp_port
    self.udp_port = udp_port

    # Criando sockets TCP e UDP
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind nos sockets
    self.tcp_socket.bind((self.host, self.tcp_port))
    self.udp_socket.bind((self.host, self.udp_port))

    # Configurando o socket TCP para escutar conexões
    self.tcp_socket.listen(5)  # Máximo de 5 conexões pendentes

    self.pending = []
    self.sequence_number = 0

  # No TCP, recebe apenas leituras. 
  def handle_tcp(self):
    print(f"Servidor TCP escutando em {self.host}:{self.tcp_port}")
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

  def handle_udp(self):
    print(f"Servidor UDP escutando em {self.host}:{self.udp_port}")
    while True:
        data, _ = self.udp_socket.recvfrom(1024)
        m = CommitRequestMessage.from_json(data.decode())
        print(f"send[={m.type}; de=; para={self.udp_port}, t.id={m.tid}]")
        
        h = self.handle_message(m)

        # Respondendo diretamente para o cliente.
        self.udp_socket.sendto(h.to_json().encode(), (m.origin[0], m.origin[1]))
        print(f"recv[={h.type}; de={self.udp_port}; para=]")

        self.deliver(m)

  def deliver(self, message):
    
    # Se a mensagem for a próxima esperada, entregamos imediatamente
    if message.seq == self.sequence_number + 1:
        print(f"deliverd[id={message.tid}, seq={message.seq}]")
        self.sequence_number += 1

        # Depois de entregar a mensagem, verificamos se há mais mensagens para entregar
        self._deliver_next()

    # Caso contrário, armazenamos a mensagem no buffer
    else:
        # print(f"Server {self.udp_port} buffering message: {content} (out of order)")
        self.pending.append(message)

  def _deliver_next(self):
      # Verifica se a próxima mensagem está no buffer
      while (self.sequence_number + 1) in [msg.seq for msg in self.pending]:
          # Encontra a próxima mensagem que pode ser entregue
          next_message = next(msg for msg in self.pending if msg.seq == self.sequence_number + 1)
          self.pending = [msg for msg in self.pending if msg.seq != self.sequence_number + 1]  # Remove a mensagem do buffer
          print(f"deliverd[id={next_message.tid}, seq={self.sequence_number}]")
          self.sequence_number += 1


  def start(self):
      # Criando threads para TCP e UDP
      tcp_thread = threading.Thread(target=self.handle_tcp)
      udp_thread = threading.Thread(target=self.handle_udp)

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

  s1 = Server(host, tcp_port, udp_port)
  s1.start()



