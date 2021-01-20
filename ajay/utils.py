import sys
from asyncstdlib.builtins import iter as aiter, anext, map, zip
from asyncstdlib.itertools import tee, zip_longest

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

async def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    await anext(b, None)
    return zip(a, b)