from file_func import controllo_validita_url
from file_func import crea_dizionario

def test_controllo_validita_url():
    assert controllo_validita_url('https://google.com')== True
    assert controllo_validita_url('http://google.com')== True
    assert controllo_validita_url('https//google.com')== False 

def test_crea_dizionario():
    output = crea_dizionario([('a', 'b'), ('c', 'd'), ('e', 'f')])
    assert isinstance(output, dict) == True
    for chiave in output.keys():
        assert isinstance(chiave, str) == True
    for valore in output.values():
        assert isinstance(valore, str) == True
