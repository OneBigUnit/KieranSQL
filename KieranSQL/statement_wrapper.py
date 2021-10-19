"""
Provides python wrappers for all SQL statements, for the user to query their SQLite database.
Also provides a selection wrapper, which provides formatting options for all data fetched from a database.
"""


from __future__ import annotations
from pprint import pformat
import sqlite3
from copy import deepcopy
from typing import Optional, Any, TYPE_CHECKING

from KieranSQL.types_wrapper import Integer, Null, ForeignKey
from KieranSQL.errors import InvalidStatement, InvalidQuery, ConnectionException, IllegalArgumentError
from KieranSQL.formatting import Formatting
from KieranSQL.column_wrapper import WhereConditionWrapper, ColumnWrapper

if TYPE_CHECKING:  # Do not import 'Table' due to circular dependancy, but still use it in type hints
  from KieranSQL.table_wrapper import Table


class SelectionWrapper(list):
  """
  A wrapper for fetched data from a database, which provides formatting options, but acts as a default list.
  """
  def __init__(self, data: list, selected_columns: list) -> None:
    self.data = data
    self.columns = selected_columns
    super().__init__(data)  # Call the 'list' class' constructor
  
  def __repr__(self) -> str:
    return pformat(self.data)  # A nicely formatted list as a string
  
  @staticmethod
  def __get_padding(column_idx: int, target_lengths: list, field: str) -> str:
    """
    Calculate and return the padding for each field to fit into its column in formatted viewing.
    """
    target_length = target_lengths[column_idx]
    field_length = len(field)
    return  "\t" * int((target_length - (field_length - (field_length % 4))) / 4)  # A tab point is present at every 4 characters - this equation calculates
                                                                                   # the number of tabs needed in tabbing

  @staticmethod
  def __convert_to_viewable_sql(field: Any, column: ColumnWrapper) -> str:
    """
    Convert all selected fields into strings for formatted viewing only.
    """
    if field is None:
      field = "NULL"
    elif type(field) == str:
      field = f"'{field}'"
    if type(column) == ForeignKey:
      return f"{column.original_column_name}[{field}]"
    else:
      return str(field)

  def format_selection(self, columns: list, selection_data: list) -> str:
    """
    Formats a selection to appear like a table.
    """
    data = [[self.__convert_to_viewable_sql(field, columns[field_idx]) for field_idx, field in enumerate(row)] for row in deepcopy(selection_data)]
    data.insert(0, [Formatting.bold(Formatting.underline(column.name)) for column in columns])  # Add table headings
    data.insert(1, ["" for _ in range(len(columns))])  # Add whitespace to emphasize headings
    result = ""
    target_lengths = [4 * round(len(max(column, key=len)) / 4) + 4 for column in list(zip(*reversed(data)))]  # Find the longest field in each column, and convert
                                                                                                              # to a target padding value for each column, achieved by
                                                                                                              # rotating the 2D matrix and performing calculations
    for row in data:
      for column_idx, field in enumerate(row):
        padding = self.__get_padding(column_idx, target_lengths, field)
        result += f"{Formatting.bold('|')}\t{field}{padding}"
      result += f"{Formatting.bold('|')}\n"
    return result

  def __str__(self) -> str:
    """
    A well formatted version of a selection of a table.
    """
    return self.format_selection(self.columns, self.data)


class SQLStatement:
  """
  A parent class for all base SQL statement wrappers, which allows for chaining of SQL queries, including 'Fetch' and 'WHERE'.
  """
  def __init__(self, table: Table, statement: str, parameterised_query_pool: Optional[list], selector: Optional[list]=None, delete: bool=False, update: bool=False) -> None:
    self.table = table
    self.parameterised_query_pool = parameterised_query_pool  # The pool of query parameters to be used in SQL execution, protecting from SQL Injection Attacks
    self.cursor = table.cursor  # The table cursor used to execute statements
    self.statement = statement
    self.selector = selector
    self.is_deleting = delete
    self.is_updating = update
  
  def __str__(self) -> str:
    """
    Returns the SQL query that is sent to the database
    """
    return f"{self.statement}\t\t{{{', '.join([str(param) for param in self.parameterised_query_pool])}}}"
  
  def Where(self, condition: Optional[WhereConditionWrapper]=None) -> SQLStatement:
    """
    A python wrapper for the SQL 'WHERE' statement, which can be used on all base SQL statements.
    This statement structure ensures that the user uses a statement structure that mimics SQL queries.
    It also ensures SQL query efficiency, as a statement won't cause the program to select all from the database and then filter with a 'WHERE' statement wrapper afterwards.
    """
    if condition is None:
      raise InvalidStatement("A WHERE statement condition cannot be empty") from None
    try:
      self.parameterised_query_pool += condition.parameterised_query_pool
    except AttributeError:
      raise InvalidStatement("A WHERE statement must be passed a valid condition") from None
    self.statement += f" WHERE {condition}"
    if self.is_deleting or self.is_updating:
      self.execute()
    return self
  
  def Fetch(self) -> SelectionWrapper:
    """
    Indicicates that a 'SELECT' query has been fully built and needs to be executed.
    This is required, as it is impossible for the program to detect when a 'SELECT' statement is finished without the user explicitly stating it.
    It also ensures that user queries mimic the same query structure as SQL.
    """
    if self.selector is None:  # If nothing is selected
      raise InvalidStatement("Cannot fetch without selected columns") from None
    self.execute()
    data = [list(record) for record in self.cursor.fetchall()]
    self.to_python_types(data)
    return SelectionWrapper(data, self.selector)  # Return selection wrapper for added formatting options
  
  def execute(self) -> None:
    """
    Executes a built and finalized SQL query.
    """
    if self.table.output_queries:
      print(f"{self}\n")
    try:
      self.cursor.execute(self.statement, self.parameterised_query_pool)
    except sqlite3.OperationalError as error:
      raise InvalidQuery(f"The following query was invalid: {self}\nFrom SQLite3: {error}") from None
    except sqlite3.ProgrammingError:
      raise ConnectionException("Cannot operate on a database without an active connection") from None
    except sqlite3.IntegrityError:
      raise IllegalArgumentError("A foreign key column was provided with a non-existant value") from None
  
  def to_python_types(self, data: list) -> None:
    """
    Convert all fetched database data to valid Python types in place.
    """
    for record_idx, record in enumerate(data):
      for column_idx, (column, field) in enumerate(zip(self.selector, record)):
        if field == "NULL":
          column_type = Null()
        else:
          column_type = column.type
        data[record_idx][column_idx] = column_type.convert_to_python(field)


class SelectWrapper(SQLStatement):
  """
  Base SQL statement wrapper, for selecting data in a database.
  """
  def __init__(self, selector: list, table: Table) -> None:
    super().__init__(table, f"SELECT {', '.join([column.name for column in selector])} FROM {table.table_name}", [], selector=selector)


class DeleteWrapper(SQLStatement):
  """
  Base SQL statement wrapper, for deleting data from a database.
  """
  def __init__(self, table: Table) -> None:
    super().__init__(table, f"DELETE FROM {table.table_name}", [], delete=True)


class InsertIntoWrapper(SQLStatement):
  """
  Base SQL statement wrapper, for inserting data into a database.
  """
  def __init__(self, table: Table, data: dict) -> None:
    data = self.__fill_all_columns(table.columns, data)
    values = self.extract_sql_safe_values([column.type for column in table.columns], data)
    data = {column.name: value for column, value in data.items()}
    columns = ', '.join(list(data.keys()))
    protected_values = f"{', '.join(['?' for value in values])}"  # Build SQL Injection Safe section of the query
    super().__init__(table, f"INSERT INTO {table.table_name} ({columns}) VALUES ({protected_values})", [str(value) for value in values])
    super().execute()  # Execute the statement, as it cannot be built on
  
  @staticmethod
  def extract_sql_safe_values(columns: list, data: dict) -> list:
    """
    Convert all python values into their respective SQL safe types for a valid query to be built.
    """
    return_values = []
    for idx, value in enumerate(list(data.values())):
      column_wrapper = list(data.keys())[idx]
      column_idx = columns.index(column_wrapper.type)
      column_wrapper = columns[column_idx]
      column_wrapper.validate(value)  # Validate that each field is valid
      return_values.append(column_wrapper.convert_to_sql(value))
    return return_values
  
  @staticmethod
  def __fill_all_columns(all_columns: list, data: dict) -> dict:
    """
    Convert all empty columns in an insertion query into SQL safe NULL values.
    """
    return_data = {}
    data_columns = list(data.keys())  # Predefine keys to eliminate multiple redundant calls
    data_values = list(data.values())  # Predefine values to eliminate multiple redundant calls
    relative_column_indexes = [[str(column) for column in all_columns].index(str(data_column)) for data_column in data_columns]
    search_idx = 0
    for column_idx, column in enumerate(all_columns):
      if isinstance(column.type, Integer) and column.type.is_primary_key:  # SQLite auto-increments any Integer Primary Key column, so do not set it to NULL if it exists
        continue
      if not search_idx >= len(relative_column_indexes):  # If not all passed in columns have been been checked
        if column_idx != relative_column_indexes[search_idx]:  # If a column isn't passed in, set it's field values to NULL
          return_data[column] = Null()
        else:  # If a column is a passed in, set its values to the passed in values, and increment the column search index
          return_data[column] = data_values[search_idx]
          search_idx += 1
      else:
        return_data[column] = Null()  # If all passed in columns have been checked, set the remaining column field values to NULL
    return return_data


class UpdateWrapper(SQLStatement):
  """
  Base SQL statement wrapper, for updating data in a database.
  """
  def __init__(self, table: Table, data: dict) -> None:
    keys = [column.name for column in list(data.keys())]
    values = self.extract_sql_safe_values([column.type for column in table.columns], data)
    statement_base = ", ".join([f"{key} = ?" for key in keys])
    super().__init__(table, f"UPDATE {table.table_name} SET {statement_base}", [str(value) for value in values], update=True)

  
  @staticmethod
  def extract_sql_safe_values(columns: list, data: dict) -> list:
    """
    Convert all python values into their respective SQL safe types for a valid query to be built.
    """
    return_values = []
    for idx, value in enumerate(list(data.values())):
      column_wrapper = list(data.keys())[idx]
      column_idx = columns.index(column_wrapper.type)
      column_wrapper = columns[column_idx]
      column_wrapper.validate(value)  # Validate that each field is valid
      return_values.append(column_wrapper.convert_to_sql(value))
    return return_values
