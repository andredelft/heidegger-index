from jsonschema import validate
from pathlib import Path
import yaml

WORKING_DIR = Path("validation")
INDEX_DIR = WORKING_DIR.parent / "index"
INDEX_FILE = INDEX_DIR / "heidegger-index.yml"
SCHEMA_FILE = WORKING_DIR / "schema.yml"


def validate_yaml(file, schema):
    validate(yaml.safe_load(file), yaml.safe_load(schema))


def validate_index():
    with open(INDEX_FILE) as f:
        with open(SCHEMA_FILE) as s:
            validate_yaml(f, s)


if __name__ == "__main__":
    validate_index()
