from lark import Lark
from lark.reconstruct import Reconstructor as LarkReconstructor, _isalnum
from dataclasses import dataclass
from immutabledict import immutabledict
from .utils import force_iterable, collapse_spaces

@dataclass(frozen=True)
class ACLCommunicativeAct:
    type: str
    parameters: immutabledict = immutabledict()

    @staticmethod
    def new(type, **params):
        return ACLCommunicativeAct(
            type,
            immutabledict(params)
        )

    def to_acl_string(self):
        tree = python_parser.parse(repr(self))
        tokens = string_writer.reconstruct_token_list(tree)
        return collapse_spaces(' '.join(tokens))

@dataclass(frozen=True)
class AgentIdentifier:
    name: str
    addresses: tuple = tuple()
    resolvers: tuple = tuple()
    parameters: immutabledict = immutabledict()

    @staticmethod
    def new(name, addresses=tuple(), resolvers=tuple(), **params):
        return AgentIdentifier(
            name,
            tuple(force_iterable(addresses)),
            tuple(force_iterable(resolvers)),
            immutabledict(params)
        )

class Reconstructor(LarkReconstructor):
    # Same code as reconstruct, but return y instead of ''.join(y)
    def reconstruct_token_list(self, tree, postproc=None):
        x = self._reconstruct(tree)
        if postproc:
            x = postproc(x)
        y = []
        prev_item = ''
        for item in x:
            if prev_item and item and _isalnum(prev_item[-1]) and _isalnum(item[0]):
                y.append(' ')
            y.append(item)
            prev_item = item
        return y

string_parser = Lark.open("grammars/fipa_acl.lark", rel_to=__file__, start="acl_communicative_act")
string_writer = Reconstructor(string_parser)
python_parser = Lark.open("grammars/fipa_acl_py.lark", rel_to=__file__, start="acl_communicative_act")
python_writer = Reconstructor(python_parser)

def parse(message_str):
    tree = string_parser.parse(message_str)
    msg_repr = python_writer.reconstruct(tree)
    return eval(msg_repr)