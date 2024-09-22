# web_scraping.py
import requests
from bs4 import BeautifulSoup
import PyPDF2
import re

# PRIMA richiesta, entra il 1° link del CIR -> esce la risposta dal sito che contiene il json della prima metà degli ingredienti
def get_initial_response(url):
    response = requests.get(url + "FetchCIRReports/")
    response.raise_for_status()
    return response

# entra la risposta della prima metà --> esce la stringa che servirà per ottenere la seconda metà degli ingredienti.
def get_paging_cookie(response):
    return response.json()["pagingcookie"] + "&page=2"

# SECONDA richiesta, entra il link per la seconda metà -> esce la risposta che contiene il json della seconda metà degli ingredienti.
def get_second_response(url, cookie):
    return requests.get(url + "?&pagingcookie=" + cookie)

# entrano i due json di ingredienti -> escono due liste che corrispondo alla informazioni degli ingredienti e i loro nomi (non duplicati)
def extract_ingredients(documento1, documento2):
    ingredienti_cir, check, nomi = [], [], []
    for el in documento1 + documento2:
        if (el["pcpc_ingredientname"] not in check) and (el["pcpc_ciringredientid"]):
            ingredienti_cir.append(el)
            nomi.append(el["pcpc_ingredientname"])
            check.append(el["pcpc_ingredientname"])
    return ingredienti_cir, nomi

# entrano gli ingredienti presenti e quello richiesto -> esce nulla oppure solo le informazioni dell'ingrediente trovato
def find_ingredient(ingredienti_cir, ingrediente_richiesto):
    for record in ingredienti_cir:
        if ingrediente_richiesto == record["pcpc_ingredientname"]:
            return record
    return None

# TERZA richiesta, entrano le componenti per ottenere la pagina dell'ingrediente richiesto -> esce il testo della pagina relativa all'ingrediente.
def get_ingredient_report(url, ID_ingrediente):
    response = requests.get(url + "cir-ingredient-status-report/?id=" + ID_ingrediente)
    response.raise_for_status()
    return response.text

# Entra la pagina dell'ingrediente -> esce la componente per la richiesta del pdf report oppure nulla.
def extract_pdf_link(html_contenuto):
    soup = BeautifulSoup(html_contenuto, "lxml")
    table = soup.find('table')
    links = table.find_all('a', href=True)
    for link in links:
        if not link['href'].startswith('javascript:alert'):
            return link['href']
    return None

# pdf_processing.py

# QUARTA richiesta, entrano le componenti per il pdf -> Esce il report.
def download_pdf(url, pdf_path):
    response = requests.get(url)
    response.raise_for_status()
    if response.status_code == 200:
        with open(pdf_path, 'wb') as f:
            f.write(response.content)

# entra il percorso del pdf scaricato -> esce il contenuto formato testo del pdf.
def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        full_text = ''
        for page in reader.pages:
            full_text += page.extract_text().replace('\n', ' ')
    return full_text

# text_analysis.py

# Entrano il contenuto e ciò che stiamo cercando -> esce una lista che ha come elemento il valore, l'unità di misura e il contesto dell'indice.
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

# Entra il testo contenente l'indice da trovare -> esce una parte di esso (200 caratteri)
def estrai_contesto(testo, inizio, fine, valore):
    prima = testo[max(0, inizio - 100):inizio].split()[-10:]
    dopo = testo[fine: fine + 100].split()[:10]
    contesto = " ".join(prima + [valore] + dopo)
    return contesto.strip()

# main.py
def main():
    suffisso_url = "https://cir-reports.cir-safety.org/"
    response1 = get_initial_response(suffisso_url) # Risposta che contiene il json relativo alla prima metà degli ingredienti + cookie.
    cookie = get_paging_cookie(response1) # Si ottiene la stringa per la seconda metà degli ingredienti.
    response2 = get_second_response(response1.url, cookie) # Risposta che contiene il json relativo alla seconda metà degli ingredienti .
    
    # Si ottengono i due json di ingredienti dalle risposte (prima e seconda metà).
    documento1 = response1.json()["results"]
    documento2 = response2.json()["results"]
    
    # Informazioni e nomi ingredienti non duplicati.
    ingredienti_cir, nomi = extract_ingredients(documento1, documento2)
    
    ingrediente_richiesto = input("Inserire il nome dell'ingrediente da trovare: ")
    # Info dell'ingrediente richiesto.
    ingrediente_trovato = find_ingredient(ingredienti_cir, ingrediente_richiesto)
    
    if ingrediente_trovato:
        ID_ingrediente = ingrediente_trovato["pcpc_ingredientid"]
        # Pagina dell'ingrediente richiesto.
        html_contenuto = get_ingredient_report(suffisso_url, ID_ingrediente)
        
        # Stringa per il link del pdf.
        pdf_link = extract_pdf_link(html_contenuto)
        if pdf_link:
            # Creazione file report.pdf
            download_pdf(suffisso_url + pdf_link[2:], 'report.pdf')
            # Contenuto pdf formato testo.
            full_text = extract_pdf_text('report.pdf')
            
            # Output finale da caricare in un CSV.
            risultati_noael = trova_valori(full_text, "NOAEL")
            print(risultati_noael)
    else:
        print("Ingrediente non trovato.")

if __name__ == "__main__":
    main()