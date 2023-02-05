import sys
from enum import Enum


class LogLevel(Enum):
    VERBOSE = 2
    DEBUG = 1
    NORMAL = 0


global LOG_LEVEL
LOG_LEVEL = LogLevel.NORMAL


def E(tag='', msg=''):
    sys.stderr.write(f'E[{tag}]:{msg}\n')


def W(tag='', msg=''):
    sys.stdout.write(f'W[{tag}]:{msg}\n')


def I(tag='', msg=''):
    sys.stdout.write(f'I[{tag}]:{msg}\n')


def D(tag='', msg=''):
    if LOG_LEVEL.value >= LogLevel.DEBUG.value:
        sys.stdout.write(f'D[{tag}]:{msg}\n')


def V(tag='', msg=''):
    if LOG_LEVEL.value >= LogLevel.VERBOSE.value:
        sys.stdout.write(f'I[{tag}]:{msg}\n')


def set_level(level: LogLevel):
    global LOG_LEVEL
    LOG_LEVEL = level


def debug():
    global LOG_LEVEL
    LOG_LEVEL = LogLevel.DEBUG


def verbose():
    global LOG_LEVEL
    LOG_LEVEL = LogLevel.VERBOSE


def reset():
    LOG_LEVEL = LogLevel.NORMAL
