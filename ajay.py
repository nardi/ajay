import sys, asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Action types.
from collections import namedtuple

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "message"])

Print = PrintAction
Send = SendAction

# IO setup.
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
    async for action in func(inbox):
        if isinstance(action, SendAction):
            print(f"-{name}-  Executing send action")
            print(f"-{name}-  Connecting to other agent...")
            outbox = await connect_agent(action.to)
            print(f"-{name}-  Sending message")
            await outbox.send(action.message)
        elif isinstance(action, PrintAction):
            print(f"-{name}-  {action.text}")
    print(f"-{name}-  Agent finished")

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

async def sender(inbox):
    yield Print("Started")
    
    await sleep(1)

    yield Print("Sending message")
    yield Send(receiver_port, b"Hello")

    yield Print("Done")

async def receiver(inbox):
    yield Print("Started")

    yield Print("Waiting for message")
    message = await inbox.recv()
    yield Print(f"Received message: {message}")

    yield Print("Done")

async def main():
    await gather(
        run_agent("Rick", receiver_port, receiver),
        run_agent("Sally", sender_port, sender)
    )

run(main())