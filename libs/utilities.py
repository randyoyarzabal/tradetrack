import json
import sys
import os
from os import system, name


class HiddenPrints:
    # Credit: https://stackoverflow.com/a/45669280
    # Modified to be configurable to be enabled or not.
    def __init__(self, enable=True):
        self.enable = enable

    def __enter__(self, ):
        if self.enable:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enable:
            sys.stdout.close()
            sys.stdout = self._original_stdout


def clear():
    # Credit: https://www.geeksforgeeks.org/clear-screen-python/
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def get_config():
    config = None
    config_filename = os.getenv('CONFIG_FILE')
    if os.path.isfile(config_filename):
        with open(config_filename, encoding='utf-8', errors='ignore') as config_fh:
            config = json.load(config_fh, strict=False)
    else:
        raise FileNotFoundError("{} was not found.".format(config_filename))
    return config
