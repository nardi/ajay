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

from asyncio import gather

async def receiver(inbox, act, sender_addr):
    await print("Started")

    await print("Waiting for message")
    async for message in inbox:
        await print(f"Received message: {message}")
        assert isinstance(message, MessagePercept)
        assert message.sender == sender_addr
        assert message.content == b"Hello"
        break

    await print("Done")

async def sender(inbox, act, receiver_addr):
    await print("Started")

    await print("Sending message")
    await send(receiver_addr, b"Hello")

    await print("Done")

@pytest.mark.asyncio
async def test_agent_message(unused_tcp_port_factory):
    receiver_port = unused_tcp_port_factory()
    sender_port = unused_tcp_port_factory()
    
    await gather(
        run_agent("Rick", receiver_port, receiver,
            sender_addr=local_address(sender_port)),
        run_agent("Sally", sender_port, sender,
            receiver_addr=local_address(receiver_port))
    )
