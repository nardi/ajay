### Kind of messy fix on Windows. 
# TODO: better place to put this?
import sys, asyncio

def fix_event_loop():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

fix_event_loop()
###

from zmq import PULL, PUSH
import zmq.asyncio as zmq
# TODO: change to more appropriate serialization.
# Using dumps and loads.
import pickle as serialize
from collections.abc import AsyncGenerator

from .actions import PrintAction, SendAction, ReadAction
from .percepts import MessagePercept, ReadPercept
from .utils import eprint

context = zmq.Context()

async def produce_percepts(socket, internal_percepts):
    while len(internal_percepts) > 0 or not socket.closed:
        for p in internal_percepts:
            yield p
        external_percept = serialize.loads(await socket.recv())
        yield external_percept

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

### TODO: maybe rewrite whole thing using aioreactive instead of async generators?

class GeneratorWrapper:
    def __init__(self, gen):
        self.gen = gen

    def __aiter__(self):
        self.value = yield from self.gen

async def run_agent(name, port, func, **kwargs):
    eprint(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    eprint(f"-{name}-  Starting agent")
    ## TODO: find better way to manage and merge internal + external percepts.
    ## (use aioreactive?)
    internal_percepts = []
    perceptual_loop = produce_percepts(inbox, internal_percepts)

    async def process_action(act):
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
        elif isinstance(act, ReadAction):
            with open(act.path, "r") as f:
                contents = f.read()
                percept = ReadPercept(act.path, contents)
                internal_percepts.append(percept)

    actions = func(perceptual_loop, **kwargs)
    async for act in actions:
        # Handle nested generators (TODO: not necessary after switch to streams)
        if isinstance(act, AsyncGenerator):
            gen = GeneratorWrapper(act)
            for act in gen:
                process_action(act)
            act = await actions.asend(gen.value)
        process_action(act)
    inbox.close()
    eprint(f"-{name}-  Agent finished")
