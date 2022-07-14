import configparser
import os
from . import crypto

config = configparser.ConfigParser()
path = os.path.join('config', 'settings.ini')
config.read(path)


def get(prefix, key, encrypted=False, fallback=None):
    try:
        res = config.get(prefix, key, fallback=fallback)
        return crypto.decrypt(res) if encrypted else res
    except:
        pass
