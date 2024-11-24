#!/bin/bash

# Porta a ser verificada
PORT=65432

# Encontra os processos que estão usando a porta especificada
PIDS=$(lsof -t -i:$PORT)

# Verifica se algum processo foi encontrado
if [ -n "$PIDS" ]; then
    # Mata todos os processos encontrados
    kill -9 $PIDS
    echo "Todos os processos foram terminados."
else
    echo "Nenhum processo está usando a porta $PORT."
fi

python3 server.py