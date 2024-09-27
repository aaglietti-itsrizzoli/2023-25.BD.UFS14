# Questo è lo script che popola il nostro database con i dati INCI, tempo previsto per il completamento: circa 20 ore
# Nonostante il tempo molto lungo richiesto abbiamo fatto questa scelta per ridurre al minimo il tempo di attesa lato client
 



#region Librerie e funzioni

import re
import requests as req
import pypdf as pdf
from io import BytesIO
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from tqdm import tqdm
from bs4 import BeautifulSoup

# Definisco una funzione che mi servirà per ordinare i dati estratti dal minore al maggiore,
# considerando anche le unità di misura differenti

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

#endregion

#region Connessione DB

# Ci connettiamo al nostro database MongoDB dove verranno caricati i dati

uri = "mongodb+srv://lucagiovagnoli:t7g^Fyi7zpN!Liw@ufs13.dsmvdrx.mongodb.net/?retryWrites=true&w=majority&appName=UFS13"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['INCI']

# Qualora il DB fosse da aggiornare e non da creare si dovrebbe abilitare la seguente riga di codice:
# db.Ingredienti.drop()

#endregion

#region Ottenimento link CIR

# Prepariamo la stringa base della get http, gli header da usare e l'url di base del cir da completare

request = 'https://cir-reports.cir-safety.org/FetchCIRReports/?&pagingcookie=%26lt%3bcookie%20page%3d%26quot%3b1%26quot%3b%26gt%3b%26lt%3bpcpc_name%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_ingredientidname%20last%3d%26quot%3bPEG-50%20Stearate%26quot%3b%20first%3d%26quot%3b1%2c10-Decanediol%26quot%3b%20%2f%26gt%3b%26lt%3bpcpc_cirrelatedingredientsid%20last%3d%26quot%3b%7bC223037E-F278-416D-A287-2007B9671D0C%7d%26quot%3b%20first%3d%26quot%3b%7b940AF697-52B5-4A3A-90A6-B9DB30EF4A7E%7d%26quot%3b%20%2f%26gt%3b%26lt%3b%2fcookie%26gt%3b&page='
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
url_base = 'https://cir-reports.cir-safety.org/' 

# I dati cir si possono ottenere da due get aggiungendo i numeri 1 e 2 alla fine della stringa preparata prima

for i in range(1,3):

    # I dati sono in formato json per cui li leggiamo come tali

    table = req.get(f'{request}{i}',headers=header)
    table = table.json()

    # Cicliamo sulla lista degli oggetti json rappresentanti gli ingredienti che si trovano nella lista con chiave 'results'

    for el in tqdm(table['results']):
            
        # Siccome sono presenti duplicati non rilevanti controlliamo di non aver già inserito l'ingrediente corrente

        if not db.Ingredienti.find_one({"Nome_comune":f"{el['pcpc_ingredientname']}"}):

            # Prendiamo sia il nome comune che il nome INCI dell'ingrediente e componiamo il link alla sua pagina specifica

            Nome_comune = el['pcpc_ingredientname']
            INCI_name = el['pcpc_ciringredientname']
            link = f'https://cir-reports.cir-safety.org/cir-ingredient-status-report/?id={el['pcpc_ingredientid']}'

            # Creato il link, facciamo la get della suddetta pagina e creiamo il soup del suo html

            web_page = req.get(link,headers=header)
            page = BeautifulSoup(web_page.text,'html.parser')

            # I link relativi alle fonti sono salvati in tag 'tr' che compongono una tabella, per cui estraiamo solo quelli

            righe = page.find_all('tr')

            # Il primo tr è sempre riservato all'intestazione della tabella, per cui se è presente un solo tr significa
            # che non è presente alcuna fonte per l'ingrediente in esame

            if len(righe)>1:

                # Poichè alcune righe sono popolate da link deprecati, cicliamo su tutte le righe per trovare la prima
                # che presenti un link valido, ovvero iniziante con '../'

                for i in range(1,len(righe)):
                    riga = i      
                    report = righe[i].a['href']
                    if report[0] == '.':
                        break

                # Controlliamo che un link valido sia stato trovato

                if report[0] == '.':
                        
                        # Se in una riga è presente un link valido, componiamo il link definitivo alla fonte e ci salviamo
                        # anche la data in cui questa è stata rilasciata e il suo "nome proprio"

                        final_url = url_base + report[report.index('/')+1:]
                        date = righe[riga].find_all('td')[-1].text
                        pdf_name = righe[riga].find_all('td')[-2].text
                else:
                    final_url = ''
            else:
                final_url = ''

# endregion
            
#region Ottenimento valori NOAEL

            # Qualora avessimo trovato una fonte valida, procediamo all'estrazione dei dati

            if final_url:

                # Siccome alcune fonti sono salvate come foto, mettiamo il codice in una clausola try per gestire l'errore 
                # derivante da questa eventualità
                    
                try:

                    # Facciamo la richiesta http per avere il pddf della nostra fonte, la decodifichiamo poichè arriva in formato
                    # binario e ne estraiamo il testo

                    response = req.get(final_url,headers=header)
                    file = BytesIO(response.content)            
                    pdf_text=pdf.PdfReader(file)

                    # Creiamo un'unica stringa contenente tutto il testo del pdf ed eliminiamo i caratteri
                    # di nuova linea

                    text = ''.join([x.extract_text() for x in pdf_text.pages])
                    text = text.replace('\n',' ').replace('\r',' ')

                    # Creiamo un pattern regex che prenda le occorrenze di NOAEL seguite entro 100 caratteri da un numero
                    # sia intero che float a sua volta seguito da possibili variazioni dell'unità di misura tipica del NOAEL.
                    # Inoltre catturiamo anche 50 caratteri prima e dopo questo pattern per contesto.
                    # Tutte le occorrenze catturate vengono salvate in un iterabile


                    noael_pattern = r'(.{0,50}\bNOAEL\b.{0,100}(\b\d+\s*[\.,]*\d*\s*.g/kg\s*[\s*bw|body\s*weight]*\s*/d[a-zA-Z]{0,3}\b).{0,50})'
                    noael_values = re.finditer(noael_pattern,text)

                    # Cicliamo sul suddetto iterabile e salviamo i dati in una lista. Avendo due gruppi di cattura nel nostro 
                    # pattern, uno per l'insieme e uno solo per il valore numerico, salviamo i dati come tuple invertendone
                    # l'ordine di cattura (salviamo il valore numerico come primo elemento della tupla)

                    temp_noaels = []
                    for el in noael_values:
                        temp_noaels.append((el.group(2),el.group(1)))

                    # Poichè il suddetto iterabile risulta True anche se vuoto, effettuiamo il controllo sulla lista 
                    # appena creata per verificare se sono stati trovati dei match validi

                    if temp_noaels:

                        # Se ho dei match, prima di tutto ordino la lista in basa alla funzione definita all'inizio.
                        # Questa operazione viene fatta sulla lista di tuple per evitare di disassociare i valori dal loro contesto

                        temp_noaels.sort(key=sorting_func)

                        # Dividiamo ora i valori dal loro contesto, mantenendo l'ordine dato

                        valori_noael = [x[0] for x in temp_noaels]
                        contesti_noael = [x[1] for x in temp_noaels]
                    else:
                        valori_noael = ''
                        contesti_noael = ''

#endregion

#region Ottenimento valori LD50
                    
                    # Ripetiamo ora la stessa operazione appena conclusa ma per i valori di LD50

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

                # Qualora una qualsiasi delle precedenti operazioni andasse in errore, assegnamo valore nullo a tutti i dati

                except:
                    valori_noael = ''
                    contesti_noael = ''
                    valori_ld50 = ''
                    contesti_ld50 = ''

            # Qualore non esistesse un link valido verso una fonte, assegnamo valore nullo a tutti i dati
                    
            else:
                valori_noael = ''
                contesti_noael = ''
                valori_ld50 = ''
                contesti_ld50 = ''

#endregion

#region Caricamento ingrediente nel database

            # Dopo aver ottenuto tutti i dati che siamo stati capaci di estrarre per un dato ingrediente
            # inseriamo un oggetto a lui corrispondente nel nostro database

            db.Ingredienti.insert_one({"Nome_comune":Nome_comune,
                                        "INCI_name":INCI_name,
                                        "main_link":link,
                                        "pdf_link":final_url,
                                        "pdf_date":date,
                                        "pdf_name":pdf_name,
                                        "valori_noael":valori_noael,
                                        "contesti_noael":contesti_noael,
                                        "valori_ld50":valori_ld50,
                                        "contesti_ld50":contesti_ld50,
                                        "pbc_data":{                      # Poichè andremo poi a usare anche pubchem inserisco anche 
                                            "page":'',                    # il campo relativo a questa fonte che verrà sovrascritto
                                            "valori":'',                  # se troveremo corrispondenze
                                            "fonti":''
                                        }
                                        })
                
#endregion





