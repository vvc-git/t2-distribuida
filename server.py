from config import Config
from operation import *
import socket
import json

class Server:
  def __init__(self, host, port):
    self.last_commit = 0
    self.db = {"chave1": ("Teste", "Version123")}
    self.host = host
    self.port = port
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind((self.host, self.port))
    self.s.listen(5)

  def receive(self):
    """
    Servidor usando Berkeley Sockets.
    """
    # Aceita uma conexão
    conn, addr = self.s.accept()
    print(f"Conectado por {addr}")

    # Recebe os dados do cliente
    data = conn.recv(2048).decode()
    if data:
      m = json.loads(data)
      print(f"Mensagem recebida: {m}")
      return conn, m

  def send(self, conn, value, version):
    m = {"value": value, "version": version}
    conn.sendall(json.dumps(m).encode())
    print("mensagem enviada:", m)

  def execute(self):
    while True:
      # Espera a requisição de LEITURA do cliente
      conn, m = self.receive()
      print(m["type"])
      if m["type"] == OperationType.READ.value:
        (value, version) = self.db[m["item"]]
        self.send(conn, value, version)
        conn.close()

# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  config = Config()
  host = config.servers["SERVER1"]["HOST"]
  port = config.servers["SERVER1"]["PORT"]

  s1 = Server(host, port)
  s1.execute()