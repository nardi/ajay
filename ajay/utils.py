import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

async def anext(agen):
    return await agen.__anext__()