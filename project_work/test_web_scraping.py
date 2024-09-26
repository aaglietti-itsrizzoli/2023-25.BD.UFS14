import pytest
from jsonschema import validate
from main import fetch_ingredient_data, find_and_extract_report, download_and_extract_pdf_text, trova_valori, estrai_contesto

# Definizione dello schema per validare la struttura dei dati degli ingredienti
ingredient_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/Welcome",
    "definitions": {
        "Welcome": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "pcpc_ingredientid": {
                    "type": "string",
                    "format": "uuid"
                },
                "pcpc_ingredientname": {
                    "type": "string"
                },
                "pcpc_ciringredientid": {
                    "type": "string",
                    "format": "uuid"
                },
                "pcpc_ciringredientname": {
                    "type": "string"
                },
                "pcpc_cirreportname": {
                    "type": "string"
                }
            },
            "required": [
                "pcpc_ciringredientid",
                "pcpc_ciringredientname",
                "pcpc_cirreportname",
                "pcpc_ingredientid",
                "pcpc_ingredientname"
            ],
            "title": "Welcome"
        }
    }
}

url = "https://cir-reports.cir-safety.org/"


def test_fetch_ingredient_data():
    """Test per verificare l'ottenimento dei dati degli ingredienti."""
    ingredienti = fetch_ingredient_data(url)
    assert len(ingredienti) > 0, "Nessun ingrediente trovato!"
    
    # Validazione della struttura del primo ingrediente
    validate_wrapper(ingredienti[0], ingredient_schema)


def validate_wrapper(instance, schema):
    try:
        validate(instance = instance, schema = schema)
        return True
    except:
        return False


def test_find_and_extract_report():
    """Test per verificare l'estrazione del report PDF di un ingrediente."""
    ingredienti = fetch_ingredient_data(url)
    
    # Selezioniamo il nome di un ingrediente specifico esistente nei dati
    ingrediente_richiesto = ingredienti[0]["pcpc_ingredientname"]
    pdf_link = find_and_extract_report(ingredienti, ingrediente_richiesto, url)
    
    # Verificare che il link del PDF non sia vuoto
    assert pdf_link is not None, f"Link PDF non trovato per l'ingrediente {ingrediente_richiesto}"
    assert pdf_link.startswith("https://"), "Il link del PDF non è valido!"


def test_download_and_extract_pdf_text():
    """Test per scaricare un PDF e verificare l'estrazione del testo."""
    # Link di esempio per il test. Sostituire con un link specifico se necessario
    pdf_link = url + "view-attachment/?id=94742a1a-c561-614f-9f89-14ce58abfc0b"
    
    # Scaricare e estrarre il contenuto del PDF
    testo = download_and_extract_pdf_text(pdf_link, pdf_path="test_report.pdf")
    
    # Verificare che il testo estratto non sia vuoto
    assert len(testo) > 0, "Il testo del PDF non è stato estratto correttamente!"


def test_trova_valori():
    """Test per cercare i valori di NOAEL nel testo del PDF."""
    # Esempio di testo tratto da un PDF (può essere sostituito con un vero testo estratto)
    testo_pdf = """
    NOAEL 50 mg/kg/d, seguito da ulteriori dati con NOAEL 100 mg/kg/d. 
    Gli studi dimostrano che NOAEL è associato a un valore di 200 mg/kg.
    """
    
    # Verificare che i valori di NOAEL vengano trovati correttamente
    risultati = trova_valori(testo_pdf, "NOAEL")
    assert len(risultati) > 0, "Nessun valore di NOAEL trovato!"
    assert risultati[0][0] == "50 mg", "Valore NOAEL non trovato correttamente nel testo!"
    

def test_estrai_contesto():
    """Test per verificare l'estrazione del contesto di un valore specifico."""
    testo_pdf = """
    Questo è un esempio di testo che contiene un valore specifico come NOAEL 50 mg/kg, seguito da ulteriori dati.
    """
    
    # Estrarre il contesto per il valore NOAEL 50 mg/kg
    valore = "50"
    inizio = testo_pdf.find(valore)
    fine = inizio + len(valore)
    contesto = estrai_contesto(testo_pdf, inizio, fine, valore)
    
    # Verifica che il contesto estratto contenga la parola chiave e un contesto significativo
    assert valore in contesto, f"Il valore {valore} non è presente nel contesto estratto!"
    assert "NOAEL" in contesto, "Il contesto estratto non contiene il termine NOAEL!"
