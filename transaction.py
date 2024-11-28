from enum import Enum
import uuid

class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    COMMIT = "commit"
    ABORT = "abort"

class Operation:
    def __init__(self, type: OperationType, item=None, value=None):
        if not isinstance(type, OperationType):
            raise ValueError("type must be an instance of OperationType Enum")
        self.type = type
        self.item = item
        self.value = value
        self.result = None

    # Getter para 'type'
    def get_type(self):
        return self.type

    # Getter para 'item'
    def get_item(self):
        return self.item

    # Getter para 'value'
    def get_value(self):
        return self.value
    
class Transaction:
    def __init__(self, operations):
        self.operations = operations
        self.id = uuid.uuid4()
