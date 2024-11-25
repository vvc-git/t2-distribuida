import json
import socket
import threading

from config import Config


class Sequencer():
  def __init__(self, host, udp_port, servers):
    super().__init__()
    self.host = host
    self.udp_port = udp_port

    self.seq_number = 0
    # Criando sockets TCP e UDP
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind nos sockets
    self.udp_socket.bind((self.host, self.udp_port))

    self.servers = servers

  def handle_message(self, m, addr):
    for ipport in self.servers.values():
      host = ipport["HOST"]
      port = ipport["UDPPORT"]
      self.udp_socket.sendto(json.dumps((m, self.seq_number, addr)).encode(), (host, port))
      print("Mensagem COMMIT (UDP) enviada para os Servidores", host + ":" + str(port))


  def handle_udp(self):
    print(f"Sequenciador UDP escutando em {self.host}:{self.udp_port}")
    while True:
        data, addr = self.udp_socket.recvfrom(1024)
        m = json.loads(data.decode())
        print(f"Mensagem UDP recebida de {addr}: {m}")
        self.handle_message(m, addr)

        # ----------- SEQUENCIADOR NÃO RESPONDE --------------
        # response = json.dumps(self.handle_message(m, addr))
        # print("response", response)
        # self.udp_socket.sendto(response.encode(), addr)

  def start(self):
    # Criando threads para TCP e UDP
    udp_thread = threading.Thread(target=self.handle_udp)

    # Iniciando as threads
    udp_thread.start()

    # Aguardando o término das threads (opcional)
    udp_thread.join()

# Executa o servidor
if __name__ == "__main__":
  # Seta os IP e Portas 
  config = Config()
  host = config.sequencer["SEQUENCER"]["HOST"]
  udp_port = config.sequencer["SEQUENCER"]["UDPPORT"]

  s1 = Sequencer(host, udp_port, config.servers)
  s1.start()
  # s1.execute()