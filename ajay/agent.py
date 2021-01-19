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
from collections.abc import Coroutine
from asyncio import Queue as AsyncQueue
import aioreactive as rx

from .actions import PrintAction, SendAction, ReadAction
from .percepts import MessagePercept, ReadPercept, ResultPercept
from .utils import eprint, anext

from .actions import GenericAction, wrap_coroutine

from .actions import act_context
from .percepts import percepts_context

context = zmq.Context()

async def produce_percepts(socket, internal_percepts):
    while not internal_percepts.empty() or not socket.closed:
        while not internal_percepts.empty():
            yield await internal_percepts.get()
        external_percept = serialize.loads(await socket.recv())
        yield external_percept

async def connect_agent(port):
    outbox = context.socket(PUSH)
    outbox.connect(f"tcp://localhost:{port}")
    return outbox

async def run_agent(name, port, func, **kwargs):
    eprint(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    eprint(f"-{name}-  Starting agent")
    internal_percepts = AsyncQueue()
    percepts = produce_percepts(inbox, internal_percepts)

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
                await internal_percepts.put(percept)
        elif isinstance(act, GenericAction):
            percept = ResultPercept(await act.coroutine)
            await internal_percepts.put(percept)
    action_obs = rx.AsyncAnonymousObserver(process_action)

    actions = rx.AsyncSingleSubject()
    async def act(action):
        if isinstance(action, Coroutine):
            # If action is a coroutine, wrap it as
            # a GenericAction and retrieve its result
            # as the first percept.
            genact = wrap_coroutine(action)
            await actions.asend(genact)
            percept = await anext(percepts)
            return percept.result
        else:
            await actions.asend(action)
    
    percepts_context.set(percepts)
    act_context.set(act)

    async with await actions.subscribe_async(action_obs):
        await func(percepts, act, **kwargs)

    inbox.close()
    eprint(f"-{name}-  Agent finished")
