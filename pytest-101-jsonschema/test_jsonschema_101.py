import json
from jsonschema import validate, ValidationError
import pytest

def func():
    transformed_data = {
        #"greeting": "Welcome to quicktype!",
        "instructions": [
            "AAAAA"
        ]
    }
    return transformed_data


def test_answer():
    with pytest.raises(ValidationError) as excinfo:
        data_to_be_validated = func()
        schema_file = open('test_jsonschema.contract.out.json')
        schema = json.load(schema_file)
        validate(instance=data_to_be_validated, schema=schema)
    assert "'greeting' is a required property" in str(excinfo.value)
