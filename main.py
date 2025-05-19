import json
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from src.main import main
from utils import validate_config

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config_path>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        with open(config_path) as f:
            config: dict = json.load(f)
        if validate_config(config=config, func=main):
            config = {k: int(v) for k, v in config.items()}
            main(**config)

    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)
