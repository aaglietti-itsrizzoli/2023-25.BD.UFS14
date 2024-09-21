from main import get_initial_response, extract_ingredients

def test_get_initial_response():
    response = get_initial_response("https://example.com/")
    assert response.status_code == 200

def test_extract_ingredients():
    documento1 = [{"pcpc_ingredientname": "Ing1", "pcpc_ciringredientid": "ID1"}]
    documento2 = [{"pcpc_ingredientname": "Ing2", "pcpc_ciringredientid": "ID2"}]
    ingredienti, nomi = extract_ingredients(documento1, documento2)
    assert len(ingredienti) == 2
    assert "Ing1" in nomi and "Ing2" in nomi