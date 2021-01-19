from collections import namedtuple
from contextvars import ContextVar

act_context = ContextVar('act')

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "content"])

GenericAction = namedtuple("GenericAction", ["name", "args", "coroutine"])

def wrap_coroutine(cr):
    """ Wraps a coroutine as a GenericAction. """
    name = cr.__qualname__
    args = cr.cr_frame.f_locals
    return GenericAction(name, args, cr)

Print = PrintAction
Send = SendAction

def action_function(Action):
    async def func(*args, **kwargs):
        await act_context.get()(Action(*args, **kwargs))
    return func

print = action_function(Print)
send = action_function(Send)