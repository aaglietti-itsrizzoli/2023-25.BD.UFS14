from file_func import controllo_validita_url

def test_controllo_validita_url():
    assert controllo_validita_url('https://google.com')== True
    assert controllo_validita_url('http://google.com')== True
    assert controllo_validita_url('https//google.com')== False