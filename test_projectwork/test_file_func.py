from file_func import controllo_validita_url
from file_func import crea_dizionario

#test di assert
def test_controllo_validita_url():
    assert controllo_validita_url('https://google.com')== True
    assert controllo_validita_url('http://google.com')== True
    assert controllo_validita_url('https//google.com')== False 

#test validita json
def test_crea_dizionario():
    output = crea_dizionario([('a', 'b'), ('c', 'd'), ('e', 'f')])
    assert isinstance(output, dict) == True
    for chiave in output.keys():
        assert isinstance(chiave, str) == True
    for valore in output.values():
        assert isinstance(valore, str) == True

#snapshot
def test_snapshot(snapshot):
    snapshot.snapshot_dir = 'snapshots_proj'
    output_2 = str(crea_dizionario([('a', 'b'), ('c', 'd'), ('e', 'f')]))
    snapshot.assert_match(output_2, 'proj_output.txt')