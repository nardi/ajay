import sys
from asyncstdlib.builtins import anext

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)