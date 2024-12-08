from random import randint
import time
from messages import CommitResponseMessage
from transaction import Operation, OperationType, Transaction
import socket_handler as sh
"""
Teste 4:
- O Cliente 0 faz C. 
- O Cliente 1 faz C. 
- O Sequenciador recebe a mesagem de 0 primeiro e 1 em segundo. Para o teste, não envia a mensagem para o Servidor 0 (Forçando o Servidor 1 repassar)
- O Servidor recebe mas não entrega até estar na ordem
- Resultado: Abort da transação.
"""
def teste4client0(client):
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()
    client.show_late_delivered()
           
           
def teste4client1(client):
    # Define as operações das transações
    time.sleep(1)
    operacoes_transacao1 = [
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()
    client.show_late_delivered()


def teste4sequencer0(sequencer):
    print(f"Servidor Sequenciador escutando em: {sequencer.host}:{sequencer.udp_port}")
    lista_mensagens = list()

    # Recebe as mensagens e cria alguma ordem
    while True:
      m_raw, addr = sequencer.recv_udp(sequencer.socket)
      m = sequencer._add_seq_origin(m_raw, addr)

      # Reencaminha para todos os servidores.
      for ipport in sequencer.servers.values():
        host = ipport["HOST"]
        port = ipport["UDPPORT"]
        if port % 2 == 0:
          sequencer.send_udp(m, host, port, sequencer.socket)