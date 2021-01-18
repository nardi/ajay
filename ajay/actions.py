from collections import namedtuple

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "content"])
ReadAction = namedtuple("ReadAction", ["path"])

Print = PrintAction
Send = SendAction