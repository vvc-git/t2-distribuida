import os
from dotenv import load_dotenv



class Config:
  def __init__(self):
    # Carrega as variáveis do arquivo .env, se existir
    load_dotenv(dotenv_path="/home/victor/Desktop/2024.2/distribuida/t2-distribuida/config.env")
    self.servers = self._load_servers()
    self.clients = self._load_clients()

  def _load_clients(self):
    """
    Encontra todas as variáveis de ambiente que começam com 'CLIENT'
    e as processa em um dicionário.
    """
    clients = {}
    for key, value in os.environ.items():
      if key.startswith("CLIENT"):  # Filtra as variáveis que começam com "CLIENT"
          clients[key] = self._parse_env_variable(value)
    return clients

  def _load_servers(self):
    """
    Encontra todas as variáveis de ambiente que começam com 'SERVER'
    e as processa em um dicionário.
    """
    servers = {}
    for key, value in os.environ.items():
        if key.startswith("SERVER"):  # Filtra as variáveis que começam com "SERVER"
            servers[key] = self._parse_env_variable(value)
    return servers

  def _parse_env_variable(self, value):
    """
    Processa uma variável de ambiente no formato:
    "HOST1:192.168.1.1,PORT1:65432"
    e retorna um dicionário estruturado.
    """

    # Transforma a string em um dicionário
    config = {}
    for part in value.split(","):
        key, val = part.split(":")
        key = key.strip()
        val = val.strip()
        
        # Verifica se a chave é PORT e converte o valor para inteiro
        if key.upper() == "PORT":
            val = int(val)
        
        config[key] = val
    return config