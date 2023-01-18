# Mix from google quickstart and https://youtu.be/sVURhxyc6jE

import json
import sys
import os
from os.path import dirname, realpath

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic

sys.path.append(dirname(dirname(realpath(__file__))))
from aws_secrets import get_secret


RANGE = 'Hoja 1!1:3'


def get_categories(): 
    # Gets the secrets from AWS
    secrets = json.loads(get_secret())
    build_credentials(secrets) 
    creds = service_account.Credentials.from_service_account_file(filename = "credentials.json")
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=secrets["SPREADSHEET_ID"],
                                    range=RANGE).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
            return
        return values
    except HttpError as err:
        print(err)

def build_credentials(secrets):
    # Builds a credential file if not aviable
    files = set(os.listdir())
    if "credentials.json" not in files:
        # Builds new dictionary by compression
        credential_keys = [
            "type", "project_id", "private_key_id", "private_key", 
            "client_email", "client_id", "auth_uri", "token_uri", 
            "auth_provider_x509_cert_url", "client_x509_cert_url"]
        credentials = {x: secrets[x] for x in credential_keys}
        # For some unknown reason json adds another \n to the private_key string
        # We fix that replacing any \\n with \n
        credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
        # Writes file
        with open("credentials.json", "w") as json_file:
            json.dump(credentials, json_file, indent=2)
    

if __name__ == '__main__':
    # build_credentials()
    ic(get_categories())
    