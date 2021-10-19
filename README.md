<div id="top"></div>

<br/>
<div align="center">
  <a href="https://github.com/OneBigUnit/KieranSQL">
    <img src="Images/KieranSQL.png" alt="Logo" width="457" height="318">
  </a>

  <p align="center">
    A shallow wrapper around the inbuilt SQLite3 module, to abstract away all SQL, aiming for a consistent, simple, pythonic syntax.
    <br />
    <br />
    <a href="https://github.com/OneBigUnit/KieranSQL/blob/b889a6dc2d85f6368f01c284fd52f7bc981edbb9/Docs/Documentation.md"><strong>Explore the Docs »</strong></a>
    <br />
    <br />
  </p>
</div>


<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#getting-started">Getting Started</a></li>
      <ul>
        <li><a href="#replit">Replit</a></li>
      </ul>
    <li><a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#creating-a-table">Creating a Table</a></li>
        <li><a href="#linking-tables">Linking Tables</a></li>
      </ul>
    <li><a href="#features">Features</a></li>
      <ul>
        <li><a href="support-for-all-common-data-types">Data Type Support</a></li>
        <li><a href="support-for-all-common-sql-statements">SQL Statement Support</a></li>
        <li><a href="field-restraint-support">Field Restraint Support</a></li>
        <li><a href="data-safety">Data Safety</a></li>
        <li><a href="data-normalization-support">Data Normlaization Support</a></li>
        <li><a href="other-features">Other Features</a></li>
      </ul>
    <li><a href="#license">License</a></li>
  </ol>
</details>
## Features

Below is a list of all the features provided in the `KieranSQL` module.

### Support for all common data types



### Support for all common SQL statements



### Field Restraint Support



### Data Safety




### Data Normlaization Support



### Other Features

## Getting Started

To run this code, follow the below instructions:
* Head over to the [KieranSQL Replit](https://replit.com/@KieranLock/KieranSQL)
* Click run!


### Replit

1. Once you are viewing the project on [Replit.com](https://replit.com), you can edit any code you like
2. All source code can be found in the `KieranSQL` directory
3. For examples on how to use this module, see [Usage Examples](#usage)

<p align="right">(<a href="#top">back to top</a>)</p>


## Usage

Below are some examples of how to use `KieranSQL`.

### Creating a table

Below is how to create a simple SQLite table using KieranSQL:
```
from KieranSQL import SQLiteTable, String, Integer

@SQLiteTable()
class People:
  PersonID: Integer(primary_key=True)
  FirstName: String(30)
  LastName: String(20)
  Nationality: String(20)
```

### Linking tables

Below is how to link two tables using **foreign keys**:
```
from KieranSQL import SQLiteTable, String, Integer

@SQLiteTable()
class Nationalities:
  ID: Integer(primary_key=True)
  Name: String(20)

@SQLiteTable()
class People:
  PersonID: Integer(primary_key=True)
  FirstName: String(30)
  LastName: String(20)
  Nationality: Nationalities.ID
```

_For referencing expected syntax, please refer to the [Documentation](https://github.com/OneBigUnit/KieranSQL/blob/b889a6dc2d85f6368f01c284fd52f7bc981edbb9/Docs/Documentation.md)_

<p align="right">(<a href="#top">back to top</a>)</p>


## Features

Below is a list of all the features provided in the `KieranSQL` module.

### Support for all common data types

Support for all common data types

### Support for all common SQL statements

Support for all common SQL statements

### Field Restraint Support

Field Restraint Support

### Data Safety

Data Safety

### Data Normlaization Support

Data Normlaization Support

### Other Features

Other Features


## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>
