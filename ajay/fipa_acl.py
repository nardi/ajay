from lark import Lark, Transformer
from collections import namedtuple
from immutabledict import immutabledict
from decimal import Decimal
from urllib.parse import urlparse, urlunparse, ParseResult as URLParseResult
import re

from .utils import force_iterable

def false_to_empty_string(val, prepend=""):
    return "" if not val else f"{prepend}{val}"

WORD_REGEX = r"[^\x00-\x20()#0-9-@][^\x00-\x20()]*"

def str_value(val, maybe_word=True):
    if isinstance(val, str):
        if maybe_word and re.search(WORD_REGEX, val):
            return val
        else:
            return f'"{val}"'
    elif isinstance(val, URLParseResult):
        return f'{urlunparse(val)}'
    else:
        return str(val)

def str_sequence(seq, prepend=""):
    return f"{prepend} ( sequence {' '.join(map(str_value, seq))} )" if seq else ""

def raise_dashes(s):
    return s.replace("_", "-")

class ACLCommunicativeAct(namedtuple("ACLCommunicativeAct", ["type", "parameters"])):
    def __str__(self):
        newline_if_params = "\n" if self.parameters else ""
        params = (newline_if_params
            + "\n".join([f"  :{raise_dashes(p)} {str_value(v, p != 'content')}" for p, v in self.parameters.items()])
            + newline_if_params)

        return f"( {raise_dashes(self.type)}{params})"

class paramdict(immutabledict):
    def __str__(self):
        return " ".join(f"{p} {v}" for p, v in self.items())

class AgentIdentifier(namedtuple("AgentIdentifier", ["name", "addresses", "resolvers", "parameters"])):
    def __new__(cls, name, addresses=tuple(), resolvers=tuple(), parameters=paramdict()):
        return super().__new__(cls, name,
            tuple(force_iterable(addresses)),
            tuple(force_iterable(resolvers)),
            paramdict(parameters))

    def __str__(self):
        addresses = str_sequence(self.addresses, " :addresses")
        resolvers = str_sequence(self.resolvers, " :resolvers")
        parameters = false_to_empty_string(self.parameters, " ")
                
        return f"( agent-identifier :name {self.name}{addresses}{resolvers}{parameters} )"

class acl_set(set):
    def __str__(self):
        return f"( set {' '.join(map(str, self))} )"

def none_to_empty_list(val):
    return [] if val == None else val
def none_to_empty_tuple(val):
    return tuple() if val == None else val

class ACLTransformer(Transformer):
    STRING = lambda _, t: str(t)[1:-1]
    WORD    = str
    NUMBER  = lambda _, t: Decimal(t)
    DATETIMETOKEN = str

    url     = lambda _, t: urlparse(t[0])
    url_sequence = tuple
    agent_identifier_sequence = tuple
    agent_identifier_set = acl_set

    def agent_identifier(self, tree):
        name, addresses, resolvers, *user_def = tree
        
        user_params = dict(zip(user_def[0::2], user_def[1::2])) if user_def else {}

        return AgentIdentifier(
            name,
            none_to_empty_tuple(addresses),
            none_to_empty_tuple(resolvers),
            user_params
        )

    def message(self, tree):
        msg_type, *params = tree
        param_dict = dict(map(lambda p: (p.data, p.children[0]), params))
        return ACLCommunicativeAct(msg_type.data, param_dict)

acl_parser = Lark.open("fipa_acl.lark", rel_to=__file__, start="acl_communicative_act", maybe_placeholders=True)
acl_transformer = ACLTransformer()

def parse(message_str):
    tree = acl_parser.parse(message_str)
    return acl_transformer.transform(tree)