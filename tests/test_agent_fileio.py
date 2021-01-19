from .context import ajay
import pytest, asyncio

@pytest.fixture()
def event_loop():
    loop = asyncio.SelectorEventLoop()
    yield loop
    loop.close()

from ajay import run_agent
from ajay.actions import print

import os

async def load_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

async def agent(percepts, act, file_path):
    await print("Started")

    await print(f"Loading file {file_path}")
    content = await act(load_file(file_path))

    await print(f"Contents: '{content}'")
    assert content == "I am loaded!"

    await print("Done")

@pytest.mark.asyncio
async def test_agent_io(unused_tcp_port_factory):
    port = unused_tcp_port_factory()
    
    await run_agent("Iosias", port, agent,
        file_path=os.path.join(os.path.dirname(__file__), "test_file.txt"))
