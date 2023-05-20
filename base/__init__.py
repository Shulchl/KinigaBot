import json
from os import listdir
from json import load
from os.path import dirname, abspath, join, basename, splitext

import logging
import logging.handlers

logger = logging.getLogger('kiniga')
logger.setLevel(logging.INFO)
#logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='kiniga.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

root_directory = dirname(dirname(abspath(__file__)))
config_directory = join(root_directory, "config")

def credential(file: str) -> dict:
    with open(join(config_directory, file), "r") as f:
        return load(f)

def load_config() -> dict:
    config = dict()
    for file in listdir(config_directory):
        filename, ext = splitext(file)
        if ext == ".json":
            config[filename] = credential(file)
    return config


cfg = load_config()
log = logger
