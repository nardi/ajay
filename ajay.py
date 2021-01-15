import sys, asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from asyncio import run, gather, sleep
from zmq import PULL, PUSH
import zmq.asyncio as zmq

context = zmq.Context()

receiver_port = 5555
sender_port = 6666

async def run_agent(name, port, func):
    print(f"-{name}-  Creating socket")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    print(f"-{name}-  Starting agent")
    await func(inbox)

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

async def sender(inbox):
    print("-S-  Started")
    
    await sleep(1)

    print("-S-  Connecting to other agent...")
    outbox = await connect_agent(receiver_port)

    print("-S-  Sending message")
    await outbox.send(b"Hello")

    print("-S-  Done")

async def receiver(inbox):
    print("-R-  Started")

    print("-R-  Waiting for message")
    message = await inbox.recv()
    print("-R-  Received message: %s" % message)

    print("-R-  Done")

async def main():
    await gather(
        run_agent("R", receiver_port, receiver),
        run_agent("S", sender_port, sender)
    )

run(main())