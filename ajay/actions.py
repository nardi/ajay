from collections import namedtuple

PrintAction = namedtuple("PrintAction", ["text"])
SendAction = namedtuple("SendAction", ["to", "message"])

Print = PrintAction
Send = SendAction