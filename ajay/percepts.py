from collections import namedtuple
from contextvars import ContextVar

percepts_context = ContextVar('percepts')

MessagePercept = namedtuple("MessagePercept", ["sender", "content"])
ReadPercept = namedtuple("ReadPercept", ["path", "content"])