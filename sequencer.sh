#!/bin/bash
# Limpa o terminal
clear

# Lista de portas a serem verificadas
PORTS=(2001, 3001) # Adicione as portas desejadas aqui

# Loop para verificar cada porta na lista
for PORT in "${PORTS[@]}"; do
    # Encontra os processos que estão usando a porta especificada
    PIDS=$(lsof -t -i:$PORT)

    # Verifica se algum processo foi encontrado e mata
    if [ -n "$PIDS" ]; then
        kill -9 $PIDS
    fi
done

# Executa o servidor Python
python3 sequencer.py
