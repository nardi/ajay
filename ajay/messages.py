from .fipa_acl import AgentIdentifier, parse as parse_message, ACLCommunicativeAct, acl_set
from .agent import current_agent
from .utils import force_iterable

message_types = frozenset([
    "accept_proposal",
    "agree",
    "cancel",
    "cfp",
    "confirm",
    "disconfirm",
    "failure",
    "inform",
    "not_understood",
    "propose",
    "query_if",
    "query_ref",
    "refuse",
    "reject_proposal",
    "request",
    "request_when",
    "request_whenever",
    "subscribe",
    "inform_if",
    "proxy",
    "propagate"
])

def create_message(type, receiver, sender=None, **params):
    if not sender:
        sender = current_agent.get()
    receiver = acl_set(force_iterable(receiver))
    return ACLCommunicativeAct(
        type, {
            "sender": sender,
            "receiver": receiver,
            **params
        }
    )

def create_message_of_type(type):
    def create(receiver, sender=None, **params):
        return create_message(type, receiver, sender, **params)
    return create

for t in message_types:
    globals()[t] = create_message_of_type(t)