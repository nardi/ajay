from .context import ajay

from ajay.fipa_acl import AgentIdentifier
from ajay.agent import current_agent
from ajay.messages import parse_message, inform

import re

def remove_whitespace(s):
    return re.sub(r"[ \t\f\r\n]", "", s)

in_msg = """(inform
    :sender ( agent-identifier :name i :addresses ( sequence iiop://foo.com/acc ) userparam value )
    :receiver ( set ( agent-identifier :name j ) )
    :in-reply-to q543
    :reply-by 20210214T083000000Z
    :content
        "weather (today, raining)"
    :language Prolog)
"""
# TODO: handle user-defined parameters in message.

def test_acl_parsing_writing():
    parsed_msg = parse_message(in_msg)
    out_msg = str(parsed_msg)

    assert remove_whitespace(out_msg) == remove_whitespace(in_msg)

def test_acl_create_message():
    current_agent.set(AgentIdentifier("i", "iiop://foo.com/acc", parameters={"userparam": "value"}))

    receiver = AgentIdentifier("j")

    msg = inform(receiver,
        in_reply_to="q543",
        reply_by="20210214T083000000Z",
        content="weather (today, raining)",
        language="Prolog"
    )

    out_msg = str(msg)
    assert remove_whitespace(out_msg) == remove_whitespace(in_msg)

