from .context import ajay
import pytest, asyncio

@pytest.fixture()
def event_loop():
    loop = asyncio.SelectorEventLoop()
    yield loop
    loop.close()

from ajay import run_agent
from ajay.actions import ReadAction
from ajay.percepts import ReadPercept

import os

async def load_file(percepts, file_path):
    yield ReadAction(file_path)
    percept = await percepts.__anext__()
    assert isinstance(percept, ReadPercept)
    assert percept.path == file_path
    return percept.content

async def agent(percepts, file_path):
    yield print("Started")

    yield print(f"Loading file {file_path}")
    content = yield load_file(file_path)

    yield print(f"Contents: '{content}'")
    assert content == "I am loaded!"

    yield print("Done")

@pytest.mark.asyncio
async def test_agent_io(unused_tcp_port_factory):
    port = unused_tcp_port_factory()
    
    await run_agent("Iosias", port, agent,
        file_path=os.path.join(os.path.dirname(__file__), "test_file.txt"))
