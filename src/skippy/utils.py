import os
import json

PATH_TO_CONFIG = "config/config.json"

def load_config_file(path_to_config: str | None = None) -> dict[str,str | dict]:
    """
    Load config file with projects ids and name of job to analyze
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, PATH_TO_CONFIG) if path_to_config is None else path_to_config
    print(path)
    if os.path.exists(path):
        with open(path, "r+") as config_file:
            config = json.load(config_file)
            return config
    else:
        raise Exception("Config file not found")
