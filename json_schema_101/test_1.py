# content of test_sample.py
from jsonschema import validate

def func(x):
    return x + 1


def test_answer():
    assert func(4) == 5

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

def test_function_output_with_snapshot(snapshot):
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.
    pierino=func(5)
    pierino_stringa=str(pierino)
    snapshot.assert_match(pierino_stringa, 'foo_output.txt')                              