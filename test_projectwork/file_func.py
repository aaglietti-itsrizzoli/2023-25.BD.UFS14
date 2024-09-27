import streamlit as st
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import re
from PyPDF2 import PdfReader
from io import BytesIO


#Funzione per scaricare il PDF. Utilizziamo BytesIO per convertire il pdf in binario
def scarica_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        if 'application/pdf' in response.headers.get('Content-Type', ''):
            contenuto_pdf_binario = BytesIO(response.content)
            return contenuto_pdf_binario
        else:
            st.error(f"Il contenuto scaricato da {url} non è un PDF.")
            return None
    else:
        st.error(f"Impossibile scaricare il PDF da {url}.")
        return None


#Funzione per estrarre tutto il testo dai PDF
def estrai_testo_pdf(contenuto_pdf_binario):
    reader = PdfReader(contenuto_pdf_binario)
    lunghezza_pdf = len(reader.pages)
    testo_estratto = ""
    for pagina in range(lunghezza_pdf):
        oggetto_pagina = reader.pages[pagina]
        testo_estratto += oggetto_pagina.extract_text()
    return testo_estratto


#Funzione per estrarre il contesto attorno alla parola chiave
def estrai_contesto(testo_estratto, keyword, context_lines=2):
    if testo_estratto is None:
        return []

    righe = testo_estratto.split('\n')
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)  #Permette di trovare la parola chiave comunque sia scritta

    risultati = []
    for i, riga in enumerate(righe):
        if pattern.search(riga):
            start = max(0, i - context_lines)
            end = min(len(righe), i + context_lines + 1)
            contesto = "\n".join(righe[start:end])
            contesto = pattern.sub(f"**{keyword}**", contesto)  #Parola chiave messa in grassetto
            risultati.append(contesto)
    return risultati


#Funzione per verificare se un url è valido
def controllo_validita_url(url):
    return url.startswith('http://') or url.startswith('https://')

#Funzione che crea un dizionario con link e nomi
def filtra_link_univoci(nomi_links):
    nomi_links_univoci = []
    visti = set()
    
    for n_ingr, l_ingr in nomi_links:
        if (n_ingr, l_ingr) not in visti:
            nomi_links_univoci.append((n_ingr, l_ingr))
            visti.add((n_ingr, l_ingr))
    
    diz = dict(nomi_links_univoci)
    return diz