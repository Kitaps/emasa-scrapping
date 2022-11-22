# Funtions to be used in other modules, to reduce repetitition
import json

def load_categories(company_name):
    # Recives a company name (string). 
    # Returns the correctly formatted categories (list).
    # Theese are to be used by the corresponding company getter.
    # Theese categorys are saved in the categories json of each company.
    with open(f"{company_name}_categories.json", 'r') as file:
        return json.load(file)

def format_link(string):
    # Turns string into a link, compatible with chrome
    string = string.replace("(", "%28").replace(")", "%29")
    string = string.replace("-", "_")
    return string

if __name__ == "__main__":
    string = 'https://www.autoplanet.cl/producto/Filtro-de-Aceite-Mann-Filter-Jeep-(Cod.-Ref.-HU821X)-OEM-A6421840025/110177'
    print(format_link(string))