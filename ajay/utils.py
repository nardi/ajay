import sys
from collections.abc import Iterable, Mapping
from asyncstdlib.builtins import iter as aiter, anext, map, zip
from asyncstdlib.itertools import tee, zip_longest
import re

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def force_iterable(obj):
   if (isinstance(obj, Iterable)
       and not isinstance(obj, str)
       # TODO: figure out how to filter out namedtuples s.a. AgentIdentifier. Maybe switch to dataclasses?
       and not hasattr(obj, "_fields")):
      return obj
   else:
      return [obj]

def collapse_spaces(s):
    return re.sub(r"[ \t]+", " ", s)