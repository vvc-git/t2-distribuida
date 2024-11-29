from time import sleep
from config import Config
from transaction import *
import socket
import json
import threading
import sys


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
            data = conn.recv(1024).decode()
            m = json.loads(data)
            print(f"send[=read; de={addr[1]}; para={self.tcp_port}]")
            response = json.dumps(self.handle_message(m))
            conn.sendall(response.encode())
            print(f"recv[=read; de={self.tcp_port}; para={addr[1]}]")
            conn.close()

  def handle_udp(self):
      print(f"Servidor UDP escutando em {self.host}:{self.udp_port}")
      while True:
          data, addr = self.udp_socket.recvfrom(1024)
          m, sequence_number, client_ip = json.loads(data.decode())
          print(f"send[={m['type']}; de={client_ip[1]}; para={self.udp_port}, t.id={m['transaction_id']}]")
          
          h = self.handle_message(m)

          # Respondendo diretamente para o cliente.
          self.udp_socket.sendto(json.dumps(h).encode(), (client_ip[0], client_ip[1]))
          print(f"recv[={h['type']}; de={self.udp_port}; para={client_ip[1]}]")

          self.deliver(m, sequence_number)

  def deliver(self, content, sequence_number):
    
    # Se a mensagem for a próxima esperada, entregamos imediatamente
    if sequence_number == self.sequence_number + 1:
        print(f"deliverd[id={content['transaction_id']}, seq={sequence_number}]")
        self.sequence_number += 1

        # Depois de entregar a mensagem, verificamos se há mais mensagens para entregar
        self._deliver_next()

    # Caso contrário, armazenamos a mensagem no buffer
    else:
        # print(f"Server {self.udp_port} buffering message: {content} (out of order)")
        self.pending.append((sequence_number, content))

  def _deliver_next(self):
      # Verifica se a próxima mensagem está no buffer
      while (self.sequence_number + 1) in [seq for seq, _ in self.pending]:
          # Encontra a próxima mensagem que pode ser entregue
          next_message = next(msg for seq, msg in self.pending if seq == self.sequence_number + 1)
          self.pending = [msg for msg in self.pending if msg[0] != self.sequence_number + 1]  # Remove a mensagem do buffer
          print(f"deliverd[id={next_message['transaction_id']}, seq={self.sequence_number}]")
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
      if m["type"] == OperationType.READ.value:
        (value, version) = self.db[m["item"]]
        m = {"value": value, "version": version}
        return m
      else:
        for item, value_version in m["rs"].items():
          if self.db[item][1] > value_version['version']:
            m = {"type": OperationType.ABORT.value}
            return m
        for item, value in m["ws"].items():
          version = self.db[item][1] + 1 
          update = value
          self.db[item] = (update, version)

        m = {"type": OperationType.COMMIT.value}
        return m
          
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



