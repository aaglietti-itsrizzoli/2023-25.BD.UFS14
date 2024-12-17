import requests as req
from bs4 import BeautifulSoup



def sorting_func(el):
    num = ''
    for char in el[0]:
        if char.isnumeric():
            num = num+char
        elif char in [' ','.',',']:
            pass
        elif char == 'g':
            num = int(num)*1000
        else:
            break
             
    return int(num)


def get_cir_json(i):
    request = 'https://cir-reports.cir-safety.org/FetchCIRReports/?&pagingcookie=%26lt%3bcookie%20page%3d%26quot%3b1%26quot%3b%26gt%3b%26lt%3bpcpc_name%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_ingredientidname%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_cirrelatedingredientsid%20last%3d%26quot%3b%7bC223037E-F278-416D-A287-2007B9671D0C%7d%26quot%3b%20first%3d%26quot%3b%7b940AF697-52B5-4A3A-90A6-B9DB30EF4A7E%7d%26quot%3b%20%2f%26gt%3b%26lt%3b%2fcookie%26gt%3b&page='
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    table = req.get(f'{request}{i}',headers=header)
    return table.json()

def get_ingredient_json(json,n):
    ingredienti = json['results']
    return ingredienti[n]

def get_table_link(ingrediente):
    url_base = 'https://cir-reports.cir-safety.org/cir-ingredient-status-report/?id='
    table_link = url_base+ingrediente['pcpc_ingredientid']
    return table_link


def get_source_table(web_page):
    page = BeautifulSoup(web_page,'html.parser')
    righe = page.find_all('tr')
    return righe


def get_pdf_values(lista):
    url_base = 'https://cir-reports.cir-safety.org/'
    if len(lista)>1:           

        for i in range(1,len(lista)):
            riga = i      
            report = lista[i].a['href']
            if report[0] == '.':
                break                

        if report[0] == '.':
            final_url = url_base + report[report.index('/')+1:]
            date = lista[riga].find_all('td')[-1].text
            pdf_name = lista[riga].find_all('td')[-2].text
        else:
            final_url = ''
            date = ''
            pdf_name = ''
    else:
        final_url = ''
        date = ''
        pdf_name = ''

    return {'final_url':final_url,'date':date,'pdf_name':pdf_name}