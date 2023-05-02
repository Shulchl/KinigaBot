import json

from base.struct import Config

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

with open('config.json', 'r', encoding='utf-8') as f:
    cfg = Config(json.loads(f.read()))

log = logger
