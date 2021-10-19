"""
Provides all SQL type wrappers, which convert all data to and from SQL
"""


from __future__ import annotations
from datetime import date, time
from typing import Callable, Any, Union

from KieranSQL.errors import IllegalArgumentError, InvalidColumnType
from KieranSQL.column_wrapper import ColumnWrapper


class SQL_Type:
  """
  The parent class for all SQL type wrappers
  """
  def __init__(self, query: str, primary_key: bool, nullable: bool,
  to_sql_casting_method: Callable, to_python_casting_method: Callable,
  string_repr: str) -> None:
    self.is_primary_key = primary_key
    self.is_nullable = nullable
    self.query = query
    self.to_sql = to_sql_casting_method
    self.to_python = to_python_casting_method
    self.string_repr = string_repr
    self.evaluate_is_nullable()
    self.evaluate_primary_key()
  
  def evaluate_is_nullable(self) -> None:
    if not self.is_nullable:
      self.query += " NOT NULL"
  
  def evaluate_primary_key(self) -> None:
    if self.is_primary_key:
      self.query += " PRIMARY KEY"

  def __str__(self) -> str:
    return self.string_repr
  
  def __repr__(self) -> str:
    return self.string_repr
  
  def convert_to_sql(self, item: Any) -> Any:
    """
    Default Python --> SQL conversion method
    """
    if isinstance(item, Null):  # If the item is NULL
      return item.to_sql(item, column_is_null=False)
    try:
      return self.to_sql(item)
    except ValueError:
      raise IllegalArgumentError(f"Table column cannot hold value '{item}' (Type: {type(item)})") from None
  
  def convert_to_python(self, item: Any) -> Any:
    """
    Default SQL --> Python conversion method
    """
    return self.to_python(item)
  
  def convert_to_sql_string(self, item: str) -> str:
    """
    Adds the quotations marks for SQL strings
    """
    if type(item) != str:
      raise InvalidColumnType("A column of type 'String(?)' was passed a non-string value in either assignment or comparison") from None
    return f"'{str(item)}'"
  
  def validate(self, item: Any) -> None:
    if type(item) == Null and not self.is_nullable and (not self.is_primary_key):
      raise IllegalArgumentError(f"Column of type {self} cannot contain NULL values") from None


class String(SQL_Type):
  """
  Python wrapper for SQL type VARCHAR(n)
  """
  def __init__(self, length: int, primary_key: bool=False, nullable: bool=True) -> None:
    self.length = length
    super().__init__(f"VARCHAR({self.length})", primary_key, nullable, self.convert_to_sql_string, self.convert_to_python_string, f"String({self.length})")
  
  def convert_to_python_string(self, item: str) -> str:
    return str(item[1:-1])


class Integer(SQL_Type):
  """
  Python wrapper for SQL type INTEGER
  """
  def __init__(self, primary_key: bool=False, nullable: bool=True) -> None:
    super().__init__("INTEGER", primary_key, nullable, int, int, "Integer()")


class Float(SQL_Type):
  """
  Python wrapper for SQL type REAL
  """
  def __init__(self, primary_key: bool=False, nullable: bool=True) -> None:
    super().__init__("REAL", primary_key, nullable, float, float, "Float()")


class Boolean(SQL_Type):
  """
  Python wrapper for Python type bool() (Uses INTEGER)
  """
  def __init__(self, primary_key: bool=False, nullable: bool=True) -> None:
    super().__init__("INTEGER", primary_key, nullable, self.int_to_bool_int, bool, "Boolean()")
  
  def int_to_bool_int(self, item: Union[bool, int]) -> int:  # Union so it can convert ints and bools to SQL Boolean
    """
    Python --> SQL conversion method only for the Boolean wrapper type
    """
    result = int(item)
    return result if result == 0 else 1


class Date(SQL_Type):
  """
  Python wrapper for SQL type DATE (Python equivilent datetime.date)
  """
  def __init__(self, primary_key: bool=False, nullable: bool=True) -> None:
    super().__init__("DATE", primary_key, nullable, self.convert_to_sql_string, self.to_date, "Date()")
  
  def to_date(self, item: Any) -> date:
    return date.fromisoformat(str(item[1:-1]))
  
  def convert_to_sql_string(self, item: date) -> str:
    return f"'{str(item)}'"
  

class Time(SQL_Type):
  """
  Python wrapper for SQL type DATE (Python equivilent datetime.date)
  """
  def __init__(self, primary_key: bool=False, nullable: bool=True) -> None:
    super().__init__("DATE", primary_key, nullable, self.convert_to_sql_string, self.to_time, "Time()")
  
  def to_time(self, item: Any) -> date:
    return time.fromisoformat(str(item[1:-1]))
  
  def convert_to_sql_string(self, item: time) -> str:
    return f"'{str(item)}'"


class Null(SQL_Type):
  """
  Python wrapper for SQL type NULL (Python equivilent NoneType)
  """
  def __init__(self) -> None:
    super().__init__("NULL", False, True, self.none_to_null, lambda item: None, "Null()")
  
  def none_to_null(self, item: Null, column_is_null: bool=True) -> str:
    if type(item) != Null and column_is_null:
      raise IllegalArgumentError(f"Column of type {self} cannot contain non-NULL values") from None
    return "NULL"


class ForeignKey(ColumnWrapper):
  """
  A light wrapper for wrapper types that mimics another type, but maintains foreign key status
  """
  def __init__(self, column: ColumnWrapper, original_column_name: str) -> None:
    self.original_column_name = original_column_name
    super().__init__(column.table, column.name, column.type)
  
  def __str__(self) -> str:
    return f"Foreign Key{{{self.name} [{self.type}]}}"
