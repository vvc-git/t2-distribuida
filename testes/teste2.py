import time
from transaction import Operation, OperationType, Transaction

"""
Teste 2:
- O Cliente 0 faz R e C. Só que entre o R e o C, o Cliente 1 altera chave1
- O Cliente 1 faz W e C. 
- Resultado: Abort da transação.
"""
def teste2client0(client):
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave1"),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()

    time.sleep(5)  

    # Define as operações das transações
    operacoes_transacao2 = [
      Operation(OperationType.COMMIT),

    ]

    t2 = Transaction(operacoes_transacao2)
    client.transaction = t2
    client.execute()

def teste2client1(client):
    # Define as operações das transações
    time.sleep(2)
    operacoes_transacao1 = [
      Operation(OperationType.WRITE, item="chave1", value="Teste1"),
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    client.transaction = t1
    client.execute()
