from main import extract_pdf_text

def test_extract_pdf_text(tmp_path):
    # Crea un PDF di test
    pdf_path = tmp_path / "test.pdf"
    # ... codice per creare un PDF di test ...
    
    text = extract_pdf_text(pdf_path)
    assert "Expected content" in text