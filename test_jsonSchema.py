from jsonschema import validate

# A sample schema, like what we'd get from json.load()
schema = {
    "type" : "object",
    "properties" : {
        "price" : {"type" : "number"},
        "name" : {"type" : "string"},
    },
}



""" validate(
    instance={"name" : "Eggs", "price" : "Invalid"}, schema=schema,
) """

def test_answer():
    assert validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema) == None
