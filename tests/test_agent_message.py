from .context import ajay
import pytest, asyncio

@pytest.fixture()
def event_loop():
    loop = asyncio.SelectorEventLoop()
    yield loop
    loop.close()

from ajay import run_agent
from ajay.actions import Print as print, Send as send
from ajay.percepts import MessagePercept

from asyncio import gather, sleep

async def receiver(inbox, sender_port):
    yield print("Started")

    yield print("Waiting for message")
    async for message in inbox:
        yield print(f"Received message: {message}")
        assert isinstance(message, MessagePercept)
        assert message.sender == sender_port
        assert message.content == b"Hello"
        break

    yield print("Done")

async def sender(inbox, receiver_port):
    yield print("Started")
    
    await sleep(1)

    yield print("Sending message")
    yield send(receiver_port, b"Hello")

    yield print("Done")

@pytest.mark.asyncio
async def test_agent_message(unused_tcp_port_factory):
    receiver_port = unused_tcp_port_factory()
    sender_port = unused_tcp_port_factory()
    
    await gather(
        run_agent("Rick", receiver_port, receiver, sender_port=sender_port),
        run_agent("Sally", sender_port, sender, receiver_port=receiver_port)
    )
