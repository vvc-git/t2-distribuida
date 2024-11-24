import random
from operation import *
import socket

class Transaction:
    def __init__(self, operations):
        # Lista de servidores disponíveis
        self.servers = ['Server 1']
        # Seleciona aleatoriamente um servidor
        self.selected_server = random.choice(self.servers)
        # Conjuntos de leitura (rs) e escrita (ws)
        self.operations = operations
        self.ws = {}  # Conjunto de escritas
        self.rs = {}  # Conjunto de leituras
        self.result = None
        self.cid = 0

    def send(self, m):
      # Cria o socket (IPv4, TCP)
      host = '127.0.0.1'
      port=65432
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          # Conecta ao servidor
          s.connect((host, port))
          # É bloqueante = espera até que todos os dados sejam enviados. 
          s.sendall(m.encode('utf-8'))
          # Recebe a resposta
          data = s.recv(1024)
          print(f"Resposta do servidor: {data.decode()}")

    
    def execute(self):
      for op in self.operations:
          # Se é um operação de Escrita, então salva em ws
          if op.get_type() == OperationType.WRITE:
            self.ws[op.get_item()] = op.get_value()
           # Se é um operação de Leitura, então verifica se já foi alterado localmente.
          elif op.get_type() == OperationType.READ:
            # Se foi alterado localmente, então pega esse valor local.
            if op.get_item() in self.ws:
              # A principio, não precisamos fazer nada. A transação usaria já o valor mais recente.
              print("Achou localmente")
            # Se NÃO foi alterado localmente, então SOLICITA do servidor.
            else:
              self.send("OperationType.READ" + '&' + op.get_item() + '&' + str(self.cid))
          elif op.get_type() == OperationType.COMMIT:
            print("Fazer a difusão atômica")
            break
          else: 
            self.result = OperationType.ABORT
      return False




