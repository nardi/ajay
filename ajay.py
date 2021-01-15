import sys, asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from asyncio import run, gather, sleep
from zmq import PULL, PUSH
import zmq.asyncio as zmq

async def sender():
    print("-S-  Started")
    
    await sleep(1)
    print("-S-  Connecting to server…")
    context = zmq.Context()
    socket = context.socket(PUSH)
    socket.connect("tcp://localhost:5555")

    print("-S-  Sending message")
    await socket.send(b"Hello")

    print("-S-  Done")

async def receiver():
    print("-R-  Started")

    context = zmq.Context()
    socket = context.socket(PULL)
    socket.bind("tcp://*:5555")

    print("-R-  Waiting for message")
    message = await socket.recv()
    print("-R-  Received message: %s" % message)

    print("-R-  Done")

async def main():
    await gather(receiver(), sender())

run(main())