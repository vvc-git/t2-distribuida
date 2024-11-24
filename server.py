from operation import *
import socket
import os
import psutil

class Server:
  def __init__(self):
    self.last_commit = 0
    self.db = {"chave1": ("Teste", "Version123")}
    self.host = '127.0.0.1'
    self.port=65432
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.bind((self.host, self.port))
    self.s.listen(5)

  def receive(self):
    """
    Servidor usando Berkeley Sockets.
    """
    # Aceita uma conexão
    conn, addr = self.s.accept()
    with conn:
        print(f"Conectado por {addr}")
        # Recebe os dados do cliente
        data = conn.recv(2048)
        # if not data:
        #     return False
        # return conn, data.decode()
        # print(f"Mensagem recebida: {data.decode()}")

        data.decode()
        # Dividir a string em partes com base no delimitador '&'
        parts = data.split('&')

        # Armazenar cada parte em uma variável
        operation_type = parts[0]  # "OperationType.READ"
        item_name = parts[1]       # "item_name"
        client_id = int(parts[2])  # 12345 (convertido para inteiro, se necessário)

        value = self.db[item_name][0]
        version = value = self.db[item_name][1]
        # # Envia uma resposta
        m = value + '&' + version
        conn.sendall(m.encode('utf-8'))
        print("mensagem enviada")

  def send(self, conn, value, version):
    m = value + '&' + version
    conn.sendall(m.encode('utf-8'))
    print("mensagem enviada")

  def execute(self):
    while True:
      # Espera a requisição de LEITURA do cliente
      self.receive()

      # # Dividir a string em partes com base no delimitador '&'
      # parts = data.split('&')

      # # Armazenar cada parte em uma variável
      # operation_type = parts[0]  # "OperationType.READ"
      # item_name = parts[1]       # "item_name"
      # client_id = int(parts[2])  # 12345 (convertido para inteiro, se necessário)

      # value = self.db[item_name][0]
      # version = value = self.db[item_name][1]
      # self.send(conn, value, version)

      # # Espera a requisição de SOLICITAÇÃO DE EFETIVAÇÃO do cliente
      # for op in operations:
      #   item = op.get_item()
      #   # Se a versão do banco é maior, estão a que veio está desatulizada.
      #   if self.db.get_version() > rs[op.get_item()].get_version():
      #     # Aborta
      #     pass
      #   else: 
      #     pass

# Executa o servidor
if __name__ == "__main__":
  # kill_process_by_port(65432)
  s1 = Server()
  s1.receive()