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
from zmq import PULL, PUSH
import zmq.asyncio as zmq

context = zmq.Context()

async def run_agent(name, port, func, **kwargs):
    print(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    print(f"-{name}-  Starting agent")
    async for action in func(inbox, **kwargs):
        if isinstance(action, SendAction):
            print(f"-{name}-  Executing send action")
            print(f"-{name}-  Connecting to agent at {action.to}...")
            outbox = await connect_agent(action.to)
            print(f"-{name}-  Sending message")
            await outbox.send(action.message)
            outbox.close()
        elif isinstance(action, PrintAction):
            print(f"-{name}-  {action.text}")
    
    inbox.close()
    print(f"-{name}-  Agent finished")

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox
