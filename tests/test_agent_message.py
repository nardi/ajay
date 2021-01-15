from .context import ajay
import pytest

from ajay import run_agent, PrintAction as print, SendAction as send

from asyncio import run, gather, sleep

async def receiver(inbox):
    yield print("Started")

    yield print("Waiting for message")
    message = await inbox.recv()
    yield print(f"Received message: {message}")
    assert message == b"Hello"

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
        run_agent("Rick", receiver_port, receiver),
        run_agent("Sally", sender_port, sender, receiver_port=receiver_port)
    )