from .context import ajay
import pytest

from ajay import run_agent
from ajay import PrintAction as Print
from ajay import SendAction as Send

from asyncio import run, gather, sleep

async def receiver(inbox):
    yield Print("Started")

    yield Print("Waiting for message")
    message = await inbox.recv()
    yield Print(f"Received message: {message}")
    assert message == b"Hello"

    yield Print("Done")

async def sender(inbox, receiver_port):
    yield Print("Started")
    
    await sleep(1)

    yield Print("Sending message")
    yield Send(receiver_port, b"Hello")

    yield Print("Done")

@pytest.mark.asyncio
async def test_agent_message(unused_tcp_port_factory):
    receiver_port = unused_tcp_port_factory()
    sender_port = unused_tcp_port_factory()
    
    await gather(
        run_agent("Rick", receiver_port, receiver),
        run_agent("Sally", sender_port, sender, receiver_port=receiver_port)
    )