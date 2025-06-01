import sys
import os

sys.path.insert(0, os.path.abspath("src"))
from src.ui.optimizer_app import OptimizerApp


if __name__ == "__main__":
    OptimizerApp().run()
