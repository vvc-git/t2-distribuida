from config import Config
from transaction import *
import socket
import json
from atomic_broadcast import AtomicBroadcast
import threading

class Server(AtomicBroadcast):
  def __init__(self, host, tcp_port, udp_port):
    super().__init__()
    self.last_commit = 0
    self.db = {"chave1": ("Teste", 0)}
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
    self.nextdeliver = 1

  # No TCP, recebe apenas leituras. 
  def handle_tcp(self):
        print(f"Servidor TCP escutando em {self.host}:{self.tcp_port}")
        while True:
            conn, addr = self.tcp_socket.accept()
            print(f"Nova conexão TCP de {addr}")
            data = conn.recv(1024).decode()
            m = json.loads(data)
            print(f"Mensagem TCP recebida: {m}")
            response = json.dumps(self.handle_message(m))
            conn.sendall(response.encode())
            conn.close()

  def handle_udp(self):
      print(f"Servidor UDP escutando em {self.host}:{self.udp_port}")
      while True:
          data, addr = self.udp_socket.recvfrom(1024)
          m, seq_number, client_ip = json.loads(data.decode())
          print(f"Mensagem UDP recebida de {addr}: {m}")
          
          response = json.dumps(self.handle_message(m))
          print("response", response)

          # Respondendo diretamente para o cliente.
          self.udp_socket.sendto(response.encode(), client_ip)

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
        m = {"type": "read", "value": value, "version": version}
        return m
      else:
        for item, value_version in m["rs"].items():
          if self.db[item][0] > value_version[0]:
            m = {"type": "abort"}
            print("ABORT")
            return m
        for item, value in m["ws"].items():
          version = self.db[item][1] + 1 
          update = value
          self.db[item] = (update, version)

        print("NÃO TEVE ABORT")
        m = {"type": "commit"}
        return m
           
           

             

# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  config = Config()
  host = config.servers["SERVER1"]["HOST"]
  tcp_port = config.servers["SERVER1"]["TCPPORT"]
  udp_port = config.servers["SERVER1"]["UDPPORT"]

  s1 = Server(host, tcp_port, udp_port)
  s1.start()
  # s1.execute()