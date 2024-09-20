from jsonschema import validate

schema = {
    "type" : "object",
    "properties" : {
        "price" : {"type" : "number"},
        "name" : {"type" : "string"},
    }
}

validate(
    instance={"name" : "Eggs", "price" : 34}, schema=schema,
)  

