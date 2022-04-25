from jsonschema import validate
from pathlib import Path
import yaml

WORKING_DIR = Path("validation")
INDEX_DIR = WORKING_DIR.parent / "index"
INDEX_FILE = INDEX_DIR / "heidegger-index.yml"
SCHEMA_FILE = WORKING_DIR / "schema.json"

schema_trial = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "type": "array",
    "minProperties": 1,
    "prefixItems": [
        {"type": "object",
        "properties": {
            "type": "object",
            "properties": {
                "start": {
                    "type" : "integer",
                    "minimum": 0
                },
                "end": {
                    "type" : "integer",
                    "minimum": 0
                },
                "reftype": {
                    "enum": ["r"]
                }
            },
            "required": ["start"]
        }
        },
        {"reftype": {
            "enum": ["p", "w"]
        }}
    ]
}

def validate_yaml(file, schema):
    validate(yaml.load(file), schema)

def validate_index(schema=schema_trial):
    with open(INDEX_FILE) as f:
        validate_yaml(f, schema)
