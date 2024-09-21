# web_scraping.py
import requests
from bs4 import BeautifulSoup

def get_initial_response(url):
    response = requests.get(url + "FetchCIRReports/")
    response.raise_for_status()
    return response

def get_paging_cookie(response):
    return response.json()["pagingcookie"] + "&page=2"

def get_second_response(url, cookie):
    return requests.get(url + "?&pagingcookie=" + cookie)

def extract_ingredients(documento1, documento2):
    ingredienti_cir, check, nomi = [], [], []
    for el in documento1 + documento2:
        if (el["pcpc_ingredientname"] not in check) and (el["pcpc_ciringredientid"]):
            ingredienti_cir.append(el)
            nomi.append(el["pcpc_ingredientname"])
            check.append(el["pcpc_ingredientname"])
    return ingredienti_cir, nomi

def find_ingredient(ingredienti_cir, ingrediente_richiesto):
    for record in ingredienti_cir:
        if ingrediente_richiesto == record["pcpc_ingredientname"]:
            return record
    return None

def get_ingredient_report(url, ID_ingrediente):
    response = requests.get(url + "cir-ingredient-status-report/?id=" + ID_ingrediente)
    response.raise_for_status()
    return response.text

def extract_pdf_link(html_contenuto):
    soup = BeautifulSoup(html_contenuto, "lxml")
    table = soup.find('table')
    links = table.find_all('a', href=True)
    for link in links:
        if not link['href'].startswith('javascript:alert'):
            return link['href']
    return None

# pdf_processing.py
import PyPDF2

def download_pdf(url, pdf_path):
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code == 200:
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        full_text = ''
        for page in reader.pages:
            full_text += page.extract_text().replace('\n', ' ')
    return full_text

# text_analysis.py
import re

def trova_valori(testo, indice):
    risultati = []
    pattern = rf'{indice}\D*(\d+)\s*(mg|kg)\D*(\d+)(\D{{1,10}})'
    for match in re.finditer(pattern, testo, flags=re.IGNORECASE):
        valore_numero = match.group(1)
        parola_dopo = match.group(4).strip()
        unione_valori = valore_numero + " " + parola_dopo
        contesto = estrai_contesto(testo, match.start(), match.end(), valore_numero)
        risultati.append((unione_valori, contesto))
    return risultati

def estrai_contesto(testo, inizio, fine, valore):
    prima = testo[max(0, inizio - 100):inizio].split()[-10:]
    dopo = testo[fine: fine + 100].split()[:10]
    contesto = " ".join(prima + [valore] + dopo)
    return contesto.strip()

# main.py
def main():
    suffisso_url = "https://cir-reports.cir-safety.org/"
    response1 = get_initial_response(suffisso_url)
    cookie = get_paging_cookie(response1)
    response2 = get_second_response(response1.url, cookie)
    
    documento1 = response1.json()["results"]
    documento2 = response2.json()["results"]
    
    ingredienti_cir, nomi = extract_ingredients(documento1, documento2)
    
    ingrediente_richiesto = input("Inserire il nome dell'ingrediente da trovare: ")
    ingrediente_trovato = find_ingredient(ingredienti_cir, ingrediente_richiesto)
    
    if ingrediente_trovato:
        ID_ingrediente = ingrediente_trovato["pcpc_ingredientid"]
        html_contenuto = get_ingredient_report(suffisso_url, ID_ingrediente)
        
        pdf_link = extract_pdf_link(html_contenuto)
        if pdf_link:
            download_pdf(suffisso_url + pdf_link[2:], 'report.pdf')
            full_text = extract_pdf_text('report.pdf')
            
            risultati_noael = trova_valori(full_text, "NOAEL")
            print(risultati_noael)
    else:
        print("Ingrediente non trovato.")

if __name__ == "__main__":
    main()