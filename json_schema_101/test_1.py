# content of test_sample.py
from jsonschema import validate
def json_schema():
    schema = {
        "type" : "object",
        "properties" : {
            "price" : {"type" : "number"},
            "name" : {"type" : "string"},
            },
    }
    return schema

def test_success():
    assert validate_wrapper(instance={"name" : "Eggs", "price" : 34.99}, schema=json_schema())== True  

def test_success_fail():
    assert validate_wrapper(instance={"name" : "Eggs", "price" : "ciao"}, schema=json_schema())== False    

def validate_wrapper(instance,schema):
    try:
        validate(instance=instance,schema=schema)
        return True
    except:
        return False                                