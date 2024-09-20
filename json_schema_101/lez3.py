#print('hello world')
import jsonschema

from jsonschema import validate
schema = {
    "type" : "object",
    "properties" : {
        "price" : {"type" : "number"},
        "name" : {"type" : "string"},
    },
}

# If no exception is raised by validate(), the instance is valid.
validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema)

#qui da errore perchè c'è un valore che doveva essere numero che è stringa
validate(
    instance={"name" : "Eggs", "price" : "Invalid"}, schema=schema,
)