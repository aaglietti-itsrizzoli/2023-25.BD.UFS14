# 2023-25.BD.UFS14

## pytest

Following https://docs.pytest.org/en/stable/getting-started.html#get-started

`pip install -U pytest`

### pytest-jsonschema caveat

The pytest plugin loads JSON Schema only from the internal package folder.

See this behavior at
- https://github.com/collective/pytest-jsonschema/blob/main/src/pytest_jsonschema/fixtures.py#L29
- https://github.com/collective/pytest-jsonschema/blob/main/src/pytest_jsonschema/schemas/__init__.py#L8

We need to copy all our JSON Schemas there likely as below

`cp *.contract.out.json /usr/local/python/3.12.6/lib/python3.12/site-packages/pytest_jsonschema/schemas`

TODO: open a feature request on https://github.com/collective/pytest-jsonschema to support external JSON schemas!
