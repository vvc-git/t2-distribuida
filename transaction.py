import json
import os
import random
import socket
import threading
from config import Config
from operation import *
from dotenv import load_dotenv

class Transaction:
    def __init__(self, cid, operations, servers):
      self.cid = cid
      self.operations = operations
      # Lista de servidores disponíveis
      self.servers = servers
      # Seleciona aleatoriamente um servidor
      self.selected_server = "SERVER" + str(random.randint(0, len(self.servers)- 1))
      # Conjuntos de leitura (rs) e escrita (ws)
      self.ws = {}  # Conjunto de escritas
      self.rs = {}  # Conjunto de leituras
      self.result = None


    def send(self, m):
      # Cria o socket (IPv4, TCP)
      host = '127.0.0.1'
      port=65432
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          # Conecta ao servidor
          s.connect((host, port))
          # É bloqueante = espera até que todos os dados sejam enviados. 
          s.sendall(m)
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
              m = {"type": "read", "item": op.get_item(), "cid":self.cid}
              self.send(json.dumps(m).encode())
          elif op.get_type() == OperationType.COMMIT:
            print("Fazer a difusão atômica")
            break
          else: 
            self.result = OperationType.ABORT
      return False

def main():
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave1"),
    ]

    config = Config()
    print(config.clients)
    print(config.servers)

    t = Transaction(config.clients["CLIENT1"], operacoes_transacao1, config.servers)

    # Cria threads para executar transações concorrentes
    thread = threading.Thread(target=t.execute)

    # Inicia as threads
    thread.start()

    # Aguarda as threads terminarem
    thread.join()


if __name__ == "__main__":
    main()

