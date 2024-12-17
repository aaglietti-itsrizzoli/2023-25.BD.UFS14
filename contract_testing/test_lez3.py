from jsonschema import validate

# A sample schema, like what we'd get from json.load()
schema = {
    "type" : "object",
    "properties" : {
        "price" : {"type" : "number"},
        "name" : {"type" : "string"},
    },
}

# If no exception is raised by validate(), the instance is valid.
#validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema)

validate(instance={"name" : "Eggs", "price" : 10}, schema=schema)

def bool_validate(instance,schema):
    try:
        validate(instance=instance,schema=schema)
        return True
    except:
        return False

# content of test_sample.py
def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4

def test_jsonschema():
    assert bool_validate({"name": "bacon","price":40},schema=schema) == True

def test_json_snapshot(snapshot):
    snapshot.snapshot_dir = 'test_dir/snapshots'
    snapshot.assert_match(str(func(5)),'func_output.txt')


frutti = '''frutto,prezzo,colore
pera,100,blu
mela,10,rossa
ananas,1000,giallo'''

def test_json_snapshot_csv(snapshot):
    snapshot.snapshot_dir = 'test_dir/snapshots'
    snapshot.assert_match(frutti,'frutti.csv')