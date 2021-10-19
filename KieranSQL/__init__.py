"""
This is the entry point of the 'KieranSQL' package.
It allows the user to access all the module's utilities, without them having to know the package structure.
"""

from KieranSQL.types_wrapper import String, Integer, Float, Boolean, Date, Time, Null
from KieranSQL.table_wrapper import SQLiteTable, connect_to
from KieranSQL.errors import InvalidStatement, InvalidQuery, InvalidColumnType, InvalidPath, ConnectionException, IllegalArgumentError, TableKeysError


if __name__ == "__main__":  # Use all imports to remove green linting
  String, Integer, Float, Boolean, Date, Time, Null
  SQLiteTable, connect_to
  InvalidStatement, InvalidQuery, InvalidColumnType, InvalidPath, ConnectionException, IllegalArgumentError, TableKeysError
