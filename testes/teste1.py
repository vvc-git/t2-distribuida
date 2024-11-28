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
    time.sleep(3)  # Função sleep corretamente chamada

    # Define as operações das transações
    operacoes_transacao2 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste1"),
      Operation(OperationType.COMMIT),
    ]

    t2 = Transaction(operacoes_transacao2)
    client.transaction = t2
    client.execute()