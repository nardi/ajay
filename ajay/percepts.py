from collections import namedtuple
from contextvars import ContextVar

percepts_context = ContextVar('percepts')

MessagePercept = namedtuple("MessagePercept", ["sender", "content"])
ResultPercept = namedtuple("ResultPercept", ["result"])