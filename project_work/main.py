import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
import json

# Testato con jsonschema
def fetch_ingredient_data(url, testing = False):
    # Prima richiesta
    response1 = requests.get(url + "FetchCIRReports/")
    response1.raise_for_status()
    documento1 = response1.json()["results"]

    # Seconda richiesta usando il cookie ottenuto
    cookie = response1.json()["pagingcookie"] + "&page=2"
    response2 = requests.get(response1.url + "?&pagingcookie=" + cookie)
    response2.raise_for_status()
    documento2 = response2.json()["results"]

    results = documento1 + documento2

    if testing:
        return results[0] if results else None
    else:
        """
        with open("ingredienti.json", "w") as file:
            json.dump(results[:5], file, indent=4)
        """
        
        return results


# Testato con snapshot e assert
def find(ingredienti, ingrediente_richiesto):
    """Trova l'ingrediente richiesto e restituisce il suo ID."""
    for record in ingredienti:
        if ingrediente_richiesto == record["pcpc_ingredientname"]:
            return record["pcpc_ingredientid"]
    return None


# Testato con assert
def extract_link_pdf(ID_ingrediente, url_base, html = None):

    if ID_ingrediente is None:
        return None

    if html is None:
    
        response = requests.get(url_base + "cir-ingredient-status-report/?id=" + ID_ingrediente)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
    else:
        soup = BeautifulSoup(html, "lxml")

    link = soup.find('table').find('a', href=True, string=lambda s: s and not s.startswith('javascript:alert'))
    extracted_link = url_base + link['href'][2:] if link else None

    return extracted_link


# Non da testare perché unisce solo le due funzioni di prima
def find_and_extract_report(ingredienti, ingrediente_richiesto, url_base):
    """Trova l'ingrediente e scarica il report PDF se disponibile."""
    # Trova l'ingrediente richiesto
    ID_ingrediente = find(ingredienti, ingrediente_richiesto)
   
    # Estrai il link del PDF
    return extract_link_pdf(ID_ingrediente, url_base)


# Non da testare perché scarica solo
def download_and_extract_pdf_text(pdf_url, pdf_path='report.pdf'):
    """Scarica e estrai il contenuto del PDF."""
    response = requests.get(pdf_url)
    response.raise_for_status()
    if response.status_code == 200:
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
    
    # Estrarre il testo dal PDF
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        full_text = ''.join([page.extract_text().replace('\n', ' ') for page in reader.pages])

    return full_text


def trova_valori(testo, indice):
    """Trova i valori di un indice nel testo del report PDF."""
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
    """Estrai una parte del contesto di un valore specifico."""
    prima = testo[max(0, inizio - 100):inizio].split()[-10:]
    dopo = testo[fine: fine + 100].split()[:10]
    contesto = " ".join(prima + [valore] + dopo)
    return contesto.strip()

def main():
    suffisso_url = "https://cir-reports.cir-safety.org/"
    
    # Ottieni i dati degli ingredienti
    ingredienti_cir = fetch_ingredient_data(suffisso_url)
    
    # Trova l'ingrediente richiesto
    ingrediente_richiesto = input("Inserire il nome dell'ingrediente da trovare: ")
    pdf_link = find_and_extract_report(ingredienti_cir, ingrediente_richiesto, suffisso_url)
    
    if pdf_link:
        # Scarica e processa il PDF
        full_text = download_and_extract_pdf_text(pdf_link)
        
        # Trova i valori di NOAEL nel testo
        risultati_noael = trova_valori(full_text, "NOAEL")
        print(risultati_noael)
    else:
        print("Ingrediente non trovato o report PDF non disponibile.")

if __name__ == "__main__":
    main()
