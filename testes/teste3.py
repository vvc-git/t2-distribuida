from random import randint
import time
from messages import CommitResponseMessage
from transaction import Operation, OperationType, Transaction
import socket_handler as sh
"""
Teste 2:
- O Cliente 0 faz R e C. Só que entre o R e o C, o Cliente 1 altera chave1
- O Cliente 1 faz W e C. 
- Resultado: Abort da transação.
"""
def teste3client0(client):
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()
    client.show_late_delivered()

           
           
def teste3client1(client):
    # Define as operações das transações
    time.sleep(1)
    operacoes_transacao1 = [
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()
    client.show_late_delivered()


def teste3sequencer0(sequencer):
    print(f"Servidor Sequenciador escutando em: {sequencer.host}:{sequencer.udp_port}")
    lista_mensagens = list()

    # Recebe as mensagens e cria alguma ordem
    while True:
      m_raw, addr = sequencer.recv_udp(sequencer.socket)
      m = sequencer._add_seq_origin(m_raw, addr)
      lista_mensagens.append(m)

      if len(lista_mensagens) > 1:
         break
    
    time.sleep(2)
    # Rencaminhas em uma ordem diferente 
    order = [1, 0]
    for i in order:
      sequencer._foward_to_servers(lista_mensagens[i])
      time.sleep(2)