# Scrapper

## Setup
1. Create Virtual Work Environment
    - In head run: `python -m venv scrapper-env`
    
2. Activate Virtual Work Environment
    - On Windows, run: `scrapper-env\Scripts\activate`
    - On Unix or MacOS, run: `source scrapper-env/bin/activate`

3. Upgrade/Update pip
    run: `python.exe -m pip install --upgrade pip`

4. Install dependencies: This reads the `requirements.txt` file and installs the required dependencies. 
    - In virtual env head Run: `python -m pip install -r requirements.txt`

## Tear down
1. Deactivate Virtual Work Environment: Depending on the OS, do the same as in `activate` but instead run the `deactivate` command
    - On Windows, run `scrapper-env\Scripts\deactivate`

## Used Libraries
- `requests`: provides easy requests to webpages to get html responses
- `BeautifulSoup`: makes reading html strings easier
- `icecream`: returns better print results
- `lxml`: parses the soup so it can be navigated with BeautifulSoup

## Deprecation notices
Since sales wants to search for products by ID instead of by category, development of the get_category module has stopped for sodimac (and not started for easy).
