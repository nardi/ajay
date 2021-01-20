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
from asyncio import get_running_loop, Queue as AsyncQueue
import aioreactive as rx
from asyncstdlib.itertools import tee

from .actions import PrintAction, SendAction
from .percepts import MessagePercept, ResultPercept
from .utils import eprint, anext

from .actions import GenericAction, wrap_coroutine

from .actions import act_context
from .percepts import percepts_context

context = zmq.Context()

def local_address(port):
    return f"tcp://localhost:{port}"

def own_address(port):
    # TODO: figure out how to find this when sending over the network.
    return local_address(port)

async def log_item(item, log):
    loop = get_running_loop()
    log.append((loop.time(), item))

async def log_iterator(it, log):
    async for item in it:
        await log_item(item, log)
        yield item

async def produce_percepts(socket, internal_percepts, port):
    while not internal_percepts.empty() or not socket.closed:
        while not internal_percepts.empty():
            yield await internal_percepts.get()
        external_percept = serialize.loads(await socket.recv())
        yield external_percept

async def connect_agent(addr):
    outbox = context.socket(PUSH)
    outbox.connect(addr)
    return outbox

async def run_agent(name, port, func, **kwargs):
    eprint(f"-{name}-  Creating socket on {port}")
    inbox = context.socket(PULL)
    inbox.bind(f"tcp://*:{port}")

    eprint(f"-{name}-  Starting agent")
    internal_percepts = AsyncQueue()
    percept_log = []
    percepts = log_iterator(produce_percepts(inbox, internal_percepts, port), percept_log)

    action_log = []
    async def process_action(act):
        await log_item(act, action_log)
        if isinstance(act, SendAction):
            eprint(f"-{name}-  Executing send action")
            eprint(f"-{name}-  Connecting to agent at {act.to}...")
            outbox = await connect_agent(act.to)
            eprint(f"-{name}-  Sending message")
            message = MessagePercept(own_address(port), act.content)
            await outbox.send(serialize.dumps(message))
            outbox.close()
        elif isinstance(act, PrintAction):
            print(f"-{name}-  {act.text}")
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
    eprint(f"-{name}-  Agent finished.")
    eprint(f"-{name}-  Percepts received: \n  {percept_log}")
    eprint(f"-{name}-  Actions performed: \n  {action_log}")

    return (percept_log, action_log)
