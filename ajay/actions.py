from collections import namedtuple

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "content"])

Print = PrintAction
Send = SendAction