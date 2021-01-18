from collections import namedtuple

MessagePercept = namedtuple("MessagePercept", ["sender", "content"])
ReadPercept = namedtuple("ReadPercept", ["path", "content"])