from .context import ajay
import pytest, asyncio

@pytest.fixture()
def event_loop():
    loop = asyncio.SelectorEventLoop()
    yield loop
    loop.close()

from ajay import run_agent, local_address
from ajay.actions import print, send
from ajay.percepts import MessagePercept

import os
from asyncio import gather
from asyncstdlib.builtins import filter

async def load_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

async def source(percepts, act):
    await print("Started")

    await print("Waiting for message")
    messages = filter(lambda p: isinstance(p, MessagePercept), percepts)
    async for msg in messages:
        file_path = msg.content
        await print(f"Received request for {file_path}")
        file_contents = await act(load_file(file_path))
        await print(f"Sending contents back to {msg.sender}")
        await send(msg.sender, file_contents)
        break

    await print("Done")

async def client(percepts, act, source_addr, file_path):
    await print("Started")

    await print("Requesting data")
    await send(source_addr, file_path)

    await print("Waiting for reply")
    messages = filter(lambda p: isinstance(p, MessagePercept), percepts)
    async for message in messages:
        if message.sender == source_addr:
            await print(f"Received reply: {message}")
            assert message.content == "I am loaded!"
            break

    await print("Done")

@pytest.mark.asyncio
async def test_agent_message(unused_tcp_port_factory):
    source_port = unused_tcp_port_factory()
    client_port = unused_tcp_port_factory()
    
    await gather(
        run_agent("Sef", source_port, source),
        run_agent("Collie", client_port, client,
            source_addr=local_address(source_port),
            file_path=os.path.join(os.path.dirname(__file__), "test_file.txt"))
    )
