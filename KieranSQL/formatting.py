"""
Provides python formatting utilities for table presentation and display in the python console.
Also provides a 'str' alternative named 'Text' which evaluates 'len()' without all formatting characters.
"""


class Text:
  """
  A 'str' alternative which evaluates 'len()' without including ANSI Escape Code Characters
  """
  def __init__(self, string: str, raw_text: str) -> None:
    self.string = string  # The text without formatting applied
    self.raw_text = raw_text  # The text with formatting applied
  
  def __str__(self) -> str:
    return str(self.raw_text)
  
  def __repr__(self) -> str:
    return f"{self.raw_text!r}"

  def __len__(self) -> int:
    return len(self.string)


class Formatting:
  """
  Python formatting utilities for table presentation and display in the python console.
  Acts as a static class.
  """
  #  Octal ANSI Escape codes for formatting
  #  --------------------------------------
  END = '\033[0m'
  BLACK = '\033[30m'
  RED = '\033[31m'
  GREEN = '\033[32m'
  YELLOW = '\033[33m'
  BLUE = '\033[34m'
  MAGENTA = '\033[35m'
  CYAN = '\033[36m'
  WHITE = '\033[37m'
  SUCCESS = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  BOLD = '\033[1m'
  DIM = '\033[2m'
  UNDERLINE = '\033[4m'
  #  --------------------------------------

  @classmethod
  def black(cls, string: str) -> Text:  # Convert to black text
    return Text(string, f"{cls.BLACK}{string}{cls.END}")

  @classmethod
  def yellow(cls, string: str) -> Text:  # Convert to yellow text
    return Text(string, f"{cls.YELLOW}{string}{cls.END}")

  @classmethod
  def blue(cls, string: str) -> Text:  # Convert to blue text
    return Text(string, f"{cls.BLUE}{string}{cls.END}")

  @classmethod
  def magenta(cls, string: str) -> Text:  # Convert to magenta text
    return Text(string, f"{cls.MAGENTA}{string}{cls.END}")

  @classmethod
  def cyan(cls, string: str) -> Text:  # Convert to cyan text
    return Text(string, f"{cls.CYAN}{string}{cls.END}")

  @classmethod
  def white(cls, string: str) -> Text:  # Convert to white text
    return Text(string, f"{cls.WHITE}{string}{cls.END}")

  @classmethod
  def success(cls, string: str) -> Text:  # Convert to shaded green text
    return Text(string, f"{cls.SUCCESS}{string}{cls.END}")

  @classmethod
  def warning(cls, string: str) -> Text:  # Convert to shaded yellow text
    return Text(string, f"{cls.WARNING}{string}{cls.END}")

  @classmethod
  def fail(cls, string: str) -> Text:  # Convert to shaded red text
    return Text(string, f"{cls.FAIL}{string}{cls.END}")

  @classmethod
  def bold(cls, string: str) -> Text:  # Convert to emboldened text
    return Text(string, f"{cls.BOLD}{string}{cls.END}")

  @classmethod
  def dim(cls, string: str) -> Text:  # Convert to dimmed text
    return Text(string, f"{cls.DIM}{string}{cls.END}")

  @classmethod
  def underline(cls, string: str) -> Text:  # Convert to underlined text
    return Text(string, f"{cls.UNDERLINE}{string}{cls.END}")

  @classmethod
  def green(cls, string: str) -> Text:  # Convert to green text
    return Text(string, f"{cls.GREEN}{string}{cls.END}")

  @classmethod
  def red(cls, string: str) -> Text:  # Convert to red text
    return Text(string, f"{cls.RED}{string}{cls.END}")
