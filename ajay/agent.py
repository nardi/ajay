### Kind of messy fix on Windows. 
# TODO: better place to put this?
import sys, asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
###

from zmq import PULL, PUSH
import zmq.asyncio as zmq

from .actions import PrintAction, SendAction

context = zmq.Context()

async def receive_messages(socket):
    while not socket.closed:
        yield await socket.recv()

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

async def run_agent(name, port, func, **kwargs):
    print(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    print(f"-{name}-  Starting agent")
    actions = func(receive_messages(inbox), **kwargs)
    async for act in actions:
        if isinstance(act, SendAction):
            print(f"-{name}-  Executing send action")
            print(f"-{name}-  Connecting to agent at {act.to}...")
            outbox = await connect_agent(act.to)
            print(f"-{name}-  Sending message")
            await outbox.send(act.message)
            outbox.close()
        elif isinstance(act, PrintAction):
            print(f"-{name}-  {act.text}")
    
    inbox.close()
    print(f"-{name}-  Agent finished")