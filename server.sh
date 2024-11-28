#!/bin/bash
# Limpa o terminal
clear

# Lê o identificador
IDENTIFICADOR=$1

# Lista de portas a serem verificadas
PORTS=(2000 3000) # Adicione as portas desejadas aqui

# Loop para verificar cada porta na lista
for PORT in "${PORTS[@]}"; do
    
    # Calcula a porta alvo como a soma da porta base e o identificador
    TARGET_PORT=$((PORT + IDENTIFICADOR))

    # Encontra os processos que estão usando a porta especificada
    PIDS=$(lsof -t -i:$TARGET_PORT)

    # Verifica se algum processo foi encontrado e mata
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS
    fi
done

# Executa o servidor Python
python3 server.py $IDENTIFICADOR
