# mapXplore

[Español](doc/es/README.md)

<img src="doc/images/Logo.jpg" width="180px">

**mapXplore** is a modular application that imports data extracted of the sqlmap to PostgreSQL or SQLite database.

Its main features are:

* Import of information extracted from sqlmap to PostgreSQL or SQLite for subsequent querying.
* Sanitized information, which means that at the time of import, it decodes or transforms unreadable information into readable information.
* Search for information in all tables, such as passwords, users, and desired information.
* Automatic export of information stored in **base64**, such as:
    * Word, Excel, PowerPoint files
    * .zip files
    * Text files or plain text information
    * Images

* Filter tables and columns by criteria.
* Filter by different types of hash functions without requiring prior conversion.
* Export relevant information to Excel or HTML

# Installation

## Requirements
* python-3.11

```bash
git clone https://github.com/daniel2005d/mapXplore
cd mapXplore
pip install -r requirements
```

# Usage

It is a modular application, and consists of the following:

* **config**: It is responsible for configuration, such as the database engine to use, import paths, among others.
* **import**: It is responsible for importing and processing the information extracted from **sqlmap**.
* **query**: It is the main module capable of filtering and extracting the required information.
    * Filter by tables
    * Filter by columns
    * Filter by one or more words
    * Filter by one or more hash functions within which are:
        * MD5
        * SHA1
        * SHA256
        * SHA3
        * ....

### Beginning
> Allows loading a default configuration at the start of the program
```bash
python engine.py [--config config.json]
```
<img src="doc/screenshot/start.png" >

## Modules

- [config](doc/en/configuration.md)
- [import](doc/en/import.md)
- [principal|search](doc/en/main.md)