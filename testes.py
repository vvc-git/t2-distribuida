from transaction import Operation, OperationType, Transaction


""" TESTE 1:
-- 2x Clientes tentam alterar a mesma chave.
-- 1x consegue e outro recebe um abort.
"""
def teste1():
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste2"),
      Operation(OperationType.COMMIT),
    ]
    operacoes_transacao2 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste2"),
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    t2 = Transaction(operacoes_transacao2)

    return t1, t2

""" TESTE 2:
-- 2x Clientes tentam alterar chaves diferentes.
-- 2x conseguem.
"""
def teste2():
    # Define as operações das transações
    operacoes_transacao1 = [
      Operation(OperationType.READ, item="chave2"),
      Operation(OperationType.WRITE, item="chave2", value="Teste2"),
      Operation(OperationType.COMMIT),
    ]
    operacoes_transacao2 = [
      Operation(OperationType.READ, item="chave1"),
      Operation(OperationType.WRITE, item="chave1", value="Teste2"),
      Operation(OperationType.COMMIT),
    ]

    t1 = Transaction(operacoes_transacao1)
    t2 = Transaction(operacoes_transacao2)

    return t1, t2
