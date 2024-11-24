import threading
import transaction
import operation
from operation import *

def main():
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave1"),
      # Operation(OperationType.WRITE, item="chave2", value=50),
      # Operation(OperationType.READ, item="chave2", value=None)
    ]

    t1 = transaction.Transaction(operacoes_transacao1)

    # Cria threads para executar transações concorrentes
    thread1 = threading.Thread(target=t1.execute)
    # thread2 = threading.Thread(target=transaction.execute_transaction, args=("Transação 2", operacoes_transacao2))

    # Inicia as threads
    thread1.start()
    # thread2.start()

    # Aguarda as threads terminarem
    thread1.join()
    # thread2.join()
    print(t1.ws)


if __name__ == "__main__":
    main()