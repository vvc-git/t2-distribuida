import time
from transaction import Operation, OperationType, Transaction

"""
Teste 1:
- O Cliente 0 faz R, W, R e C. Sendo que o segundo R é realizado localmente.
- O Cliente 0 faz R, W e C. 
- Resultado: Commit da transação.
"""
def teste1client0(client):
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste1"),
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()

    # Aguardar 3 segundos entre as transações
    time.sleep(3)  

    # Define as operações das transações
    operacoes_transacao2 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste1"),
      Operation(OperationType.COMMIT),
    ]

    t2 = Transaction(operacoes_transacao2)
    client.transaction = t2
    client.execute()

'''Comportamento padrão do sequenciador'''
def teste1sequencer0(sequencer):
    print(f"Servidor Sequenciador escutando em: {sequencer.host}:{sequencer.udp_port}")
    while True:
      m_raw, addr = sequencer.recv_udp(sequencer.socket)
      m = sequencer._add_seq_origin(m_raw, addr)
      sequencer._foward_to_servers(m)