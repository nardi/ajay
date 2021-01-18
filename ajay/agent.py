### Kind of messy fix on Windows. 
# TODO: better place to put this?
import sys, asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
###

from zmq import PULL, PUSH
import zmq.asyncio as zmq
# TODO: change to more appropriate serialization.
# Using dumps and loads.
import pickle as serialize

from .actions import PrintAction, SendAction
from .percepts import MessagePercept
from .utils import eprint

context = zmq.Context()

async def receive_messages(socket):
    while not socket.closed:
        yield serialize.loads(await socket.recv())

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

async def run_agent(name, port, func, **kwargs):
    eprint(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    eprint(f"-{name}-  Starting agent")
    actions = func(receive_messages(inbox), **kwargs)
    async for act in actions:
        if isinstance(act, SendAction):
            eprint(f"-{name}-  Executing send action")
            eprint(f"-{name}-  Connecting to agent at {act.to}...")
            outbox = await connect_agent(act.to)
            eprint(f"-{name}-  Sending message")
            message = MessagePercept(port, act.content)
            await outbox.send(serialize.dumps(message))
            outbox.close()
        elif isinstance(act, PrintAction):
            print(f"-{name}-  {act.text}")
    
    inbox.close()
    eprint(f"-{name}-  Agent finished")
