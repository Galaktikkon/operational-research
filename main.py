import os
import sys

import config

sys.path.insert(0, os.path.abspath("src"))

from src.main import main

options = {
    key: value for key, value in vars(config).items() if not key.startswith("__")
}
main(**options)
