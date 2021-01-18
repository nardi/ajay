import asyncio, random
from collections.abc import *

class TestAwaitable:
    def __await__(self):
        loop = asyncio.get_event_loop()
        fut = loop.create_future()
        fut.set_result(2)
        yield from fut
        print("Hello!")
        return 4

class GeneratorWrapper:
    def __init__(self, gen):
        self.gen = gen

    def __iter__(self):
        self.value = yield from self.gen

def print_test():
    yield 2
    print("hello!")
    return 4

async def test_await():
    print("A1")
    yield 1
    ###
    x = yield print_test()
    ###
    yield 3
    yield x
    print("A2")

async def main():
    print("M1")
    it = test_await()
    async for i in it:
        # Execute inner generator
        if isinstance(i, Generator):
            g = GeneratorWrapper(i)
            for j in g:
                print(f"value: {j}")
            i = await it.asend(g.value)
        
        print(f"value: {i}")
    print("M2")

asyncio.run(main())