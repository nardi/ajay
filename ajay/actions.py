from collections import namedtuple
from contextvars import ContextVar

act_context = ContextVar('act')

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "content"])
ReadAction = namedtuple("ReadAction", ["path"])

Print = PrintAction
Send = SendAction

def action_function(Action):
    async def func(*args, **kwargs):
        await act_context.get()(Action(*args, **kwargs))
    return func

print = action_function(Print)
send = action_function(Send)