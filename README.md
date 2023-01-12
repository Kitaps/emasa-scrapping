# Scrapper

## Setup
1. Create Virtual Work Environment
    - In head run: `python -m venv scrapper-env`
    
2. Activate Virtual Work Environment
    - On Windows, run: `scrapper-env\Scripts\activate`
    - On Unix or MacOS, run: `source scrapper-env/bin/activate`

3. Upgrade/Update pip
    - Run: `python -m pip install --upgrade pip`

4. Install dependencies: This reads the `requirements.txt` file and installs the required dependencies. 
    - In virtual env head Run: `python -m pip install -r requirements.txt`

5. Add needed credentials as environment variables
    - Edit the activate scripts at the activation path (2.):
        - In the last line add the needed passwords as: `export CREDENTIALNAME="CREDENTIAL"`
        - In the last line before the `signature block` as: `$env:CREDENTIALNAME = 'CREDENTIAL'`
    - If it does not work try:
        - `deactivate` and `activate` if needed
        - using `Powershell`   
    - todo: Make it work with `cmd` & `terminal`

## Tear down
1. Deactivate Virtual Work Environment: Depending on the OS, do the same as in `activate` but instead run the `deactivate` command
    - On Windows, run `scrapper-env\Scripts\deactivate`

## Used Libraries
- `requests`: provides easy requests to webpages to get html responses
- `BeautifulSoup`: makes reading and parsing html strings easier
- `icecream`: returns better print results
- `lxml`: parses the soup so it can be navigated with BeautifulSoup
- `pandas`: preprocess data as dataframes
    -`pyarrow`
- `snowflake-connector-python`: connects to the snowflake SQL server
- `sqlalchemy`: help reading from and writing to snowflake SQL server
    -`greenlet`
    -`snowflake-sqlalchamy`
- `xlrd`: reads excel documents


## Useful Commands
- PostgreSQL
    - In case of wrong console code page run: `chcp 1252`
        - todo: add command to `activate`
    - Login with default user: `psql -U postgres`
    - Check psql server port: `SELECT * FROM pg_settings WHERE name = 'port';`
- snowflake Worksheet:
    - Get table column names: `SELECT COLUMN_NAME FROM webscraping.information_schema.columns WHERE TABLE_NAME = 'PRODUCTS';`

## Notes
- Deprecated: Since sales wants to search by category instead of search product by ID or SKU, development of the get_product modules has stopped for all stores.
- SQL: [Snowflake does not support conditional T-SQL statements.](https://stackoverflow.com/questions/62524218/how-to-write-an-equivalent-if-else-adhoc-sql-query-in-snowflake) Which means that it accepts IF and IFF statements, but can only return values, not actions.

