import azure.functions as func
import json

if __name__ == '__main__':

    with open('cir_db.json', 'r') as file:
            table = json.load(file)

    print(table)