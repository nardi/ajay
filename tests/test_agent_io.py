from .context import ajay
import pytest, asyncio

@pytest.fixture()
def event_loop():
    loop = asyncio.SelectorEventLoop()
    yield loop
    loop.close()

from ajay import run_agent
from ajay.actions import print, send, ReadAction, act_context
from ajay.percepts import ReadPercept, percepts_context
from ajay.utils import anext

import os

async def load_file(file_path):
    await act_context.get()(ReadAction(file_path))
    percept = await anext(percepts_context.get())
    assert isinstance(percept, ReadPercept)
    assert percept.path == file_path
    return percept.content

async def agent(percepts, act, file_path):
    await print("Started")

    await print(f"Loading file {file_path}")
    content = await load_file(file_path)

    await print(f"Contents: '{content}'")
    assert content == "I am loaded!"

    await print("Done")

@pytest.mark.asyncio
async def test_agent_io(unused_tcp_port_factory):
    port = unused_tcp_port_factory()
    
    await run_agent("Iosias", port, agent,
        file_path=os.path.join(os.path.dirname(__file__), "test_file.txt"))
