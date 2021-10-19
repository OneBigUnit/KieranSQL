"""
Provides a python wrapper for SQL tables, and a class decorator that gives user defined tables all their functionality.
"""


import sqlite3
from contextlib import contextmanager
from typing import Any, Optional

from KieranSQL.column_wrapper import ColumnWrapper
from KieranSQL.statement_wrapper import SelectWrapper, InsertIntoWrapper, DeleteWrapper, SelectionWrapper, UpdateWrapper
from KieranSQL.types_wrapper import SQL_Type, String, ForeignKey
from KieranSQL.errors import InvalidColumnType, InvalidPath, ConnectionException, IllegalArgumentError, TableKeysError


class TableTemplate(type):
  """
  Table metaclass which gives the class the ability to have a custom string representation.
  """
  def __str__(self) -> str:
    """
    Fetches all data from the table and returns it in a formatted string.
    """
    with connect_to(self, commit=False):  # Do not commit in case of some bug
      result: SelectionWrapper = self.Select("*").Fetch()  # Fetch all table data
    return str(result)  # And return it in a formatted string
  
  def __repr__(self) -> str:
    """
    Returns the name of the table
    """
    return self.original_table_class.table_name


class Table(metaclass=TableTemplate):  # Uses an extended metaclass to have a custom string representation despite being a static class
  """
  A python wrapper for SQL tables, which extends the functionality of user-defined tables, and allows for usage of other 'KieranSQL' module functionality.
  """
  def __new__(cls, path: str, table_name: str) -> None:  # Use __new__ constructor as class is static
    cls.path = path
    cls.__validate_path()  # Validate that the given path for the table to be saved at is valid
    cls.output_queries = False
    cls.records = 0
    cls.table_name = table_name
    cls.raw_columns = cls.__get_columns()
    cls.original_table_class = cls.__mro__[0]
    cls.columns = [ColumnWrapper(cls.original_table_class, column_name, column_type) for column_name, column_type in cls.raw_columns.items()]
    cls.foreign_keys = cls.__find_foreign_keys()
    cls.__validate_foreign_keys()
    cls.__validate_columns()
    cls.__create_table()
    return super(Table, cls).__new__(cls)
  
  @classmethod
  def __validate_foreign_keys(cls) -> None:
    """
    Validate that any foreign key columns point to a primary key column
    """
    for fkey in cls.foreign_keys:
      if not fkey.type.type.is_primary_key:
        raise TableKeysError("A foreign key column must point to a primary key column") from None
  
  @classmethod
  def __find_foreign_keys(cls) -> list:
    """
    Finds all the foreign key columns in the table.
    """
    return [column for column in cls.columns if type(column.type) == ColumnWrapper]

  @classmethod
  def __validate_path(cls) -> None:
    """
    Validates a database path, and raises an exception if it is invalid.
    """
    if type(cls.path) != str:
      raise InvalidPath(f"A database path needs to be of type '{str}'")
    if not cls.path.endswith(".db"):
      raise InvalidPath(f"A database path needs to end with '.db'")
  
  @classmethod
  def __validate_columns(cls) -> None:
    """
    Validate that a given column's type is a valid column type, and raises and exception otherwise.
    """
    primary_keys_present = 0
    for column_type in cls.raw_columns.values():
      try:
        if column_type.is_primary_key:
          primary_keys_present += 1
      except AttributeError:  # A column was a foreign key
        pass
      if SQL_Type not in type(column_type).__bases__ and type(column_type) != ColumnWrapper:
        raise InvalidColumnType(f"A column cannot be of type '{type(column_type)}'") from None
    if not primary_keys_present:
      raise TableKeysError("A table must have a primary key present")
    elif primary_keys_present > 1:
      raise TableKeysError("A table must have only one primary key present")
  
  @classmethod
  def connect(cls) -> None:
    """
    Connects to a table, which can be used by a user directly or via a context manager.
    """
    cls.connection = sqlite3.connect(cls.path)
    cls.connection.execute("PRAGMA foreign_keys = ON")
    cls.cursor = cls.connection.cursor()
  
  @classmethod
  def disconnect(cls, commit: bool=False) -> None:
    """
    Disonnects to a table, which can be used by a user directly or via a context manager.
    """
    if commit:
      cls.connection.commit()
    cls.connection.close()

  @classmethod
  def __create_table(cls) -> None:
    """
    Generates an SQL statement to create a table, and executes it.
    """
    column_data = []
    for idx, (value_name, value_type) in enumerate(list(cls.raw_columns.items())):
      if type(value_type) == ColumnWrapper:  # If column is a foreign key
        original_column_name = value_type.name
        args = (value_type.type.length, ) if type(value_type.type) == String else ()
        value_type = type(value_type.type)(*args)  # Convert the value type to an SQL wrapper type, instead of column type
        cls.columns[idx] = ForeignKey(ColumnWrapper(cls.original_table_class, value_name, value_type), original_column_name)  # But remember that the column is a foreign key
      column_data.append(f"{value_name} {value_type.query}")
    create_statement = f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({', '.join(column_data)}"  # Build create statement
    foreign_key_statements = []
    for fkey in cls.foreign_keys:
      fkey_name = fkey.name
      reference_table = fkey.type.table
      original_column_name = fkey.type.name
      foreign_key_statements.append(f"FOREIGN KEY({fkey_name}) REFERENCES {reference_table!r}({original_column_name})")
    foreign_keys_statement = f"{', '.join(foreign_key_statements)}"
    if foreign_keys_statement:
      create_statement += f", {foreign_keys_statement}"
    with connect_to(cls, commit=False):  # Do not commit in case of some bug
      cls.cursor.execute(f"{create_statement})")
  
  @classmethod
  def Select(cls, *columns: ColumnWrapper) -> SelectWrapper:
    """
    The 'Select' statement wrapper used by a user, which calls the 'Select' python statement wrapper.
    """
    if columns == ("*", ):  # If the '*' wildcard is used, convert it to select all columns
      columns = cls.columns
    return SelectWrapper(columns, cls)
  
  @classmethod
  def InsertInto(cls, data: Optional[dict]=None, **kwargs: Any) -> InsertIntoWrapper:
    """
    The 'InsertInto' statement wrapper used by a user, which calls the 'InsertInto' python statement wrapper.
    """
    if data is None and kwargs is None:
      raise IllegalArgumentError("InsertInto must be passed some data to insert") from None
    if kwargs:  # If kwargs are given, merge them into the data dictionary
      kwargs_conversion = {column.name: column for column in cls.columns}
      kwargs = {kwargs_conversion[column_name]: value for column_name, value in kwargs.items()}
      data.update(kwargs)
    return InsertIntoWrapper(cls, data)

  @classmethod
  def Delete(cls) -> DeleteWrapper:
    """
    The 'Delete' statement wrapper used by a user, which calls the 'Delete' python statement wrapper.
    """
    return DeleteWrapper(cls)

  @classmethod
  def __get_columns(cls) -> list:
    """
    Retrieves the user-defined column data from the built-in class information (class.__dict__), for later use.
    """
    return list(cls.__dict__.values())[1]
  
  @classmethod
  def Update(cls, data: Optional[dict]=None, **kwargs: Any) -> UpdateWrapper:
    """
    The 'Update' statement wrapper used by a user, which calls the 'Update' python statement wrapper.
    """
    if data is None and kwargs is None:
      raise IllegalArgumentError("Update must be passed some data to insert") from None
    if kwargs:  # If kwargs are given, merge them into the data dictionary
      kwargs_conversion = {column.name: column for column in cls.columns}
      kwargs = {kwargs_conversion[column_name]: value for column_name, value in kwargs.items()}
      data.update(kwargs)
    return UpdateWrapper(cls, data)


def SQLiteTable(path: str="database.db") -> Table:
  """
  A class decorator to extend the functionality of a user-defined table.
  A class-decorator was used instead of inheritance so that the 'Table' class' __new__ function can be called without the user explicitly encoding that functionality.
  """
  def f(unmodified_table: Any) -> Table:  # Takes a class that may not inherit from Table, but returns an extended class such that it does
    modified_table = type(unmodified_table.__name__, (Table, ), dict(unmodified_table.__dict__))  # Dynamically generate an identical class that inherits from 'Table'
    modified_table.__new__(modified_table, path, modified_table.__name__)  # Call the 'Table' class' __new__ method to initiate the table depsite the class' static nature
    for column_name, column in zip(list(modified_table.raw_columns.keys()), modified_table.columns):
      setattr(modified_table, column_name, column)  # Set the table's columns as class attributes for later use
    return modified_table
  return f


@contextmanager
def connect_to(cls: Table, commit: bool=False, output_queries: bool=False) -> Table:
  """
  A context manager to open and close a database connection, with provided settings.
  """
  if type(commit) != bool:
    raise IllegalArgumentError(f"Context manager 'connect_to' cannot take non-boolean parameter for argument 'commit'. Given value and type: ({commit}, {type(commit)})") from None
  elif type(output_queries) != bool:
    raise IllegalArgumentError(f"Context manager 'connect_to' cannot take non-boolean parameter for argument 'output_queries'. Given value and type: ({output_queries}, {type(output_queries)})") from None
  try:
    cls.output_queries = output_queries
  except (TypeError, AttributeError):
    raise ConnectionException(f"Cannot bind to the table '{cls}'") from None
  cls.connect()  # If all checks are passed, open the connection at the beginning of the 'with' block
  try:
    yield cls  # Yield the selected table (mimics the '__enter__' function)
  finally:
    cls.output_queries = False  # Reset the database settings, in case the context manager is not used to connect in future
    cls.disconnect(commit=commit)  # After 'with' block, close the connection
