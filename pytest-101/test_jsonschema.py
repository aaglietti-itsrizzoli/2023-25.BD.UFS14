import json
from pathlib import Path

def func():
    transformed_data = {
        "greeting": "Welcome to quicktype!",
        "instructions": [
            "Type or paste JSON here",
            "Or choose a sample above",
            "quicktype will generate code in your",
            "chosen language to parse the sample data"
        ]
    }
    return json.dumps(transformed_data)


def test_answer(schema_validate_string):
    data_to_be_validated = func()
    assert schema_validate_string(data=data_to_be_validated, schema_name="test_jsonschema.contract.out", file_type="json")
