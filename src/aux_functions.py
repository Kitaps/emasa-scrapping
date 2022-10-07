# Funtions to be used in other modules, to reduce repetitition
import json

def load_categories(company_name):
    # Recives a company name (string). 
    # Returns the correctly formatted categories (list).
    # Theese are to be used by the corresponding company getter.
    # Theese categorys are saved in the categories json of each company.
    with open(f"{company_name}_categories.json", 'r') as file:
        return json.load(file)