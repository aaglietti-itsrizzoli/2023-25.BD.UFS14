import azure.functions as func
import datetime
import json
import logging
import regex as re
import pypdf as pdf
import requests as rq
from test_dir.cir_functions import get_source_table, get_pdf_values, sorting_func
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bs4 import BeautifulSoup
from io import BytesIO

app = func.FunctionApp()

@app.route(route="get_main", auth_level=func.AuthLevel.ANONYMOUS)
def get_main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    ingredient_name = req.params.get('ingredient_name')

    if not ingredient_name:

        return func.HttpResponse('Inserire il nome dell\'ingrediente da ricercare nel databse CIR')
        


    if ingredient_name:

        link = ''

        with open('cir_db.json', 'r') as file:
            table = json.load(file)

        for el in table['results'][0]:

            if el['pcpc_ingredientname'] == ingredient_name or el['pcpc_ciringredientname'] == ingredient_name:

                link = f'https://cir-reports.cir-safety.org/cir-ingredient-status-report/?id={el["pcpc_ingredientid"]}'
                payload = {'ingredient_name': ingredient_name,
                           'cir_name': el['pcpc_ciringredientname'],
                           'main_link': link}
                return func.HttpResponse(payload,mimetype='application/json')
            
            else:
                continue

        if not link:

            return func.HttpResponse({},mimetype='application/json')


    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    

@app.route(route="get_pdf_values", auth_level=func.AuthLevel.ANONYMOUS)
def get_pdf_values(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    url_base = 'https://cir-reports.cir-safety.org/'

    main_url = req.params.get('req_url')

    web_page = rq.get(main_url,headers=header)
    
    righe = get_source_table(web_page)

    payload = get_pdf_values(righe)    

    return func.HttpResponse(payload,mimetype='application/json')


@app.route(route="get_values", auth_level=func.AuthLevel.ANONYMOUS)
def get_values(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}


    pdf_link = req.params.get('pdf_link')
    payload = {'valori_noael' : '',
               'contesti_noael' : '',
               'valori_ld50' : '',
               'contesti_ld50' : ''}

    try:

        response = rq.get(pdf_link,headers=header)
        file = BytesIO(response.content)            
        pdf_text=pdf.PdfReader(file)

        text = ''.join([x.extract_text() for x in pdf_text.pages])
        text = text.replace('\n','').replace('\r','')


        noael_pattern = r'(.{0,50}\bNOAEL\b.{0,100}(\b\d+\s*[\.,]*\d*\s*.g/kg\s*[\s*bw|body\s*weight]*\s*/d[a-zA-Z]{0,3}\b).{0,50})'
        noael_values = re.finditer(noael_pattern,text)

        temp_noaels = []
        for el in noael_values:
            temp_noaels.append((el.group(2),el.group(1)))

        if temp_noaels:

            temp_noaels.sort(key=sorting_func)

            valori_noael = [x[0] for x in temp_noaels]
            contesti_noael = [x[1] for x in temp_noaels]
        else:
            valori_noael = ''
            contesti_noael = ''

        ld50_pattern = r'(.{0,50}\bLD\s*50\b.{0,100}(\b\d+\s*[\.,]*\d*\s*.g/kg[\s*bw|body\s*weight]*\b).{0,50})'
        ld50_values = re.finditer(ld50_pattern,text)
        temp_ld50s = []
        for el in ld50_values:
            temp_ld50s.append((el.group(2),el.group(1)))
        if temp_ld50s:
            temp_ld50s.sort(key=sorting_func)
            valori_ld50 = [x[0] for x in temp_ld50s]
            contesti_ld50 = [x[1] for x in temp_ld50s]
        else:
            valori_ld50 = ''
            contesti_ld50 = ''

        payload['contesti_ld50'] = contesti_ld50
        payload['contesti_noael'] = contesti_noael
        payload['valori_ld50'] = valori_ld50
        payload['valori_noael'] = valori_noael

        return func.HttpResponse(payload,mimetype='application/json')

    

    except:
        return func.HttpResponse(payload,mimetype='application/json')
        


    

@app.route(route="load_values", auth_level=func.AuthLevel.ANONYMOUS)
def load_values(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    mongo_key = req.params.get('db_key')
    values = req.params.get('value')

    uri = f'mongodb+srv://lucagiovagnoli:{mongo_key}@ufs13.dsmvdrx.mongodb.net/'
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['INCI2']

    inserimento = db.Ingredienti.insert_one(values)
    if inserimento.acknowledged:
        return func.HttpResponse(status_code=200)
    else: 
        return func.HttpResponse(status_code=404)