from main import trova_valori, estrai_contesto

def test_trova_valori():
    text = "The NOAEL was 100 mg/kg for rats."
    results = trova_valori(text, "NOAEL")
    assert len(results) == 1
    assert results[0][0] == "100 for"

def test_estrai_contesto():
    text = "This is a long text. The NOAEL was 100 mg/kg for rats. More text follows."
    context = estrai_contesto(text, 20, 50, "100")
    assert "NOAEL was 100 mg/kg for" in context