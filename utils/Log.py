import sys
from enum import Enum


class LogLevel(Enum):
    NORMAL = 0
    VERBOSE = 1

LOG_LEVEL = LogLevel.VERBOSE

def E(tag='',msg=''):
    sys.stderr.write(f'E[{tag}]:{msg}\n')

def W(tag='',msg=''):
    sys.stdout.write(f'W[{tag}]:{msg}\n')

def I(tag='',msg=''):
    sys.stdout.write(f'I[{tag}]:{msg}\n')

def set_level(level: LogLevel):
    LOG_LEVEL = level
