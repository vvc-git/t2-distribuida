import json
from enum import Enum
from transaction import OperationType

class Message:
  def __init__(self, type):
    self.type = type  # A chave "type" é sempre "read"

  def to_json(self):
    # Converte os atributos da instância para JSON
    return json.dumps(self.__dict__)

# Classe especializada ReadMessage
class ReadRequestMessage(Message):
    def __init__(self, item, cid):
      super().__init__(OperationType.READ.value)
      self.item = item                      # Atributo "item"
      self.cid = cid                        # Atributo "cid"

    def __str__(self):
        return f"ReadRequestMessage(item={self.item}, cid={self.cid}, type={self.type})"

    @classmethod
    def from_json(cls, json_str):
        # Converte uma string JSON em um objeto ReadMessage
        data = json.loads(json_str)
        # Cria e retorna uma instância da classe ReadMessage usando os dados deserializados
        return cls(item=data['item'], cid=data['cid'])

# Classe especializada ReadMessage
class ReadResponseMessage(Message):
    def __init__(self, value, version):
      super().__init__(OperationType.READ.value)
      self.value = value                     
      self.version = version

    def __str__(self):
        return f"ReadResponseMessage(value={self.value}, version={self.version}, type={self.type})"

    @classmethod
    def from_json(cls, json_str):
        # Converte uma string JSON em um objeto ReadMessage
        data = json.loads(json_str)
        # Cria e retorna uma instância da classe ReadMessage usando os dados deserializados
        return cls(value=data['value'], version=data['version'])



# Classe especializada CommitMessage
class CommitRequestMessage(Message):
    def __init__(self, cid, tid, rs, ws, seq=None, origin=None):
      super().__init__(OperationType.COMMIT.value)
      self.cid = cid                         
      self.tid = tid
      self.rs = rs
      self.ws = ws
      self.seq = seq
      self.origin = origin

    def __str__(self):
        return f"CommitRequestMessage(cid={self.cid}, tid={self.tid}, rs={self.rs}, ws={self.ws}, seq={self.seq}, origin={self.origin})"

    @classmethod
    def from_json(cls, json_str):
        # Converte uma string JSON em um objeto CommitMessage
        data = json.loads(json_str)
        # Cria e retorna uma instância da classe CommitMessage usando os dados deserializados
        return cls(cid=data['cid'], tid=data['tid'], rs=data['rs'], ws=data['ws'], seq=data['seq'], origin=data['origin'])

# Classe especializada CommitMessage
class CommitResponseMessage(Message):
    def __init__(self, tid):
      super().__init__(OperationType.COMMIT.value)
      self.transaction_id = tid

    def __str__(self):
        return f"CommitResponseMessage(transaction_id={self.transaction_id})"

    @classmethod
    def from_json(cls, json_str):
        # Converte uma string JSON em um objeto CommitMessage
        data = json.loads(json_str)
        # Cria e retorna uma instância da classe CommitMessage usando os dados deserializados
        return cls(transaction_id=data['transaction_id'])
    
# Classe especializada CommitMessage
class AbortResponseMessage(Message):
    def __init__(self, tid):
      super().__init__(OperationType.ABORT.value)
      self.transaction_id = tid

    def __str__(self):
        return f"AbortResponseMessage(transaction_id={self.transaction_id})"

    @classmethod
    def from_json(cls, json_str):
        # Converte uma string JSON em um objeto CommitMessage
        data = json.loads(json_str)
        # Cria e retorna uma instância da classe CommitMessage usando os dados deserializados
        return cls(transaction_id=data['transaction_id'])
  


