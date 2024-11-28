from enum import Enum
import uuid

class OperationType(Enum):
    READ = "READ"
    WRITE = "WRITE"
    COMMIT = "COMMIT"
    ABORT = "ABORT"


class Operation:
    def __init__(self, type: OperationType, item=None, value=None):
        if not isinstance(type, OperationType):
            raise ValueError("type must be an instance of OperationType Enum")
        self._type = type
        self._item = item
        self._value = value
        self._result = None

    # Getter para 'type' usando @property
    @property
    def type(self):
        return self._type

    # Getter para 'item' usando @property
    @property
    def item(self):
        return self._item

    # Getter para 'value' usando @property
    @property
    def value(self):
        return self._value

    # Getter para 'result' usando @property
    @property
    def result(self):
        return self._result

    # Setter para 'result' usando @result.setter
    @result.setter
    def result(self, value):
        self._result = value

class Transaction:
    def __init__(self, operations):
        self.operations = operations
        self.id = uuid.uuid4()
