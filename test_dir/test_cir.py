#region Libraries and useful functions

import cir_functions as cir
import json
from jsonschema import validate

def bool_validate(instance,schema):
    try:
        validate(instance=instance,schema=schema)
        return True
    except:
        return False
    
#endregion


def test_sorting():    
    assert cir.sorting_func(('2 mg/Kg/bw','contesto')) == 2

def test_ingredient_json():

    schema = {
    "type" : "object",
    "properties" : {
        "pcpc_ingredientid" : {"type" : "string"},
        "pcpc_ingredientname" : {"type" : "string"},
        "pcpc_ciringredientid" : {"type" : "string"},
        "pcpc_ciringredientname" : {"type" : "string"},
        "pcpc_cirreportname" : {"type" : "string"}
        },
    }

    with open('test_dir/cir_json_1.json','r') as f:
        file = json.load(f)

    istanza = cir.get_ingredient_json(file,1)

    assert bool_validate(instance=istanza,schema=schema) == True


def test_snapshot_get_table(snapshot):
    with open('test_dir/web_page_test.html') as f:
        web_page = f
    
        snapshot.snapshot_dir = 'test_dir/snapshots'
        snapshot.assert_match(str(cir.get_source_table(web_page)),'source_table_test.txt')



