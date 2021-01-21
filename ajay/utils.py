import sys
from asyncstdlib.builtins import iter as aiter, anext, map, zip
from asyncstdlib.itertools import tee, zip_longest

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
