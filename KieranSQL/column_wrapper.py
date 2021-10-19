"""
This hosts a python wrapper for Columns within an SQLite table and a python wrapper for the condition parameter in a 'Where' Statement.
This file is only for internal use.
"""

from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # Do not import 'Table' due to circular dependancy, but still use it in type hints
  from KieranSQL.types_wrapper import SQL_Type
  from KieranSQL.table_wrapper import Table


class WhereConditionWrapper:
  """
  A wrapper for conditions within 'WHERE' statements, with functionality to convert chained python boolean expressions into SQL.
  """
  def __init__(self, condition: WhereConditionWrapper, parameterised_query_pool: Optional[list]=None) -> None:
    if parameterised_query_pool is None:
      parameterised_query_pool = []
    self.condition = condition  # The boolean SQL translation
    self.parameterised_query_pool = parameterised_query_pool  # The pool of query parameters to be used in SQL execution, protecting from SQL Injection Attacks

  def __and__(self, other: WhereConditionWrapper) -> WhereConditionWrapper:  # <Boolean Condition> & <Boolean Condition>
    self.parameterised_query_pool += other.parameterised_query_pool
    self.condition += f" AND {other}"
    return self
  
  def __or__(self, other: WhereConditionWrapper) -> WhereConditionWrapper:  # <Boolean Condition> | <Boolean Condition>
    self.parameterised_query_pool += other.parameterised_query_pool
    self.condition += f" OR {other}"
    return self
  
  def __str__(self) -> str:
    return str(self.condition)


class ColumnWrapper:
  """
  A python wrapper for SQLite table columns, which evaluates boolean logic using columns as SQL statements, for execution in 'WHERE' statements.
  All columns defined in a user's table automatically utilizze this wrapper.
  """
  def __init__(self, table: Table, name: str, column_type: SQL_Type) -> None:
    self.name = name
    self.type = column_type
    self.table = table
  
  def __repr__(self):
    return f"{self.name} [{self.type}]"
  
  def __str__(self):
    return f"{self.name} [{self.type}]"
  
  def __eq__(self, other: Any) -> WhereConditionWrapper:  # <Column> == <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} = ?", [other])
  
  def __ne__(self, other: Any) -> WhereConditionWrapper:  # <Column> != <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} <> ?", [other])
  
  def __lt__(self, other: Any) -> WhereConditionWrapper:  # <Column> < <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} < ?", [other])
  
  def __le__(self, other: Any) -> WhereConditionWrapper:  # <Column> <= <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} <= ?", [other])
  
  def __gt__(self, other: Any) -> WhereConditionWrapper:  # <Column> > <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} > ?", [other])
  
  def __ge__(self, other: Any) -> WhereConditionWrapper:  # <Column> >= <Value>
    other = self.__transform_other(other)
    return WhereConditionWrapper(f"{self.name} >= ?", [other])
 
  def __hash__(self) -> int:
    """
    For wrapper use as a dictionary key
    """
    return hash(self.name)
  
  def __transform_other(self, other: Any) -> Any:
    """
    Makes values put into 'WHERE' conditions 'SQL safe'.
    """
    if other is None:
      return "NULL"
    other = self.type.convert_to_sql(other)
    return other
