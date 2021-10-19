"""
Provides all possible errors the 'KieranSQL' module can raise, for specificity
"""


class InvalidStatement(Exception):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class InvalidQuery(SyntaxError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class InvalidColumnType(TypeError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class TableKeysError(KeyError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class InvalidPath(TypeError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class ConnectionException(TypeError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)


class IllegalArgumentError(ValueError):
  def __init__(self, message: str) -> None:
    self.message = message
    super().__init__(self.message)
