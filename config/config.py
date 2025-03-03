import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value

    def get_env(self, key, default=None):
        return os.getenv(key, default)


# Create a global config instance
config = Config()