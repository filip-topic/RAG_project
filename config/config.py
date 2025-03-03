import os
import yaml

def load_config(path="config.yaml"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, path)
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

CONFIG = load_config()
