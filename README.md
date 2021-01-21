# Ajay

An [agent-oriented programming](https://en.wikipedia.org/wiki/Agent-oriented_programming) framework for Python based on asyncio (async/await). Built using [aioreactive](https://github.com/dbrattli/aioreactive) and [ZeroMQ](https://zeromq.org) ([pyzmq](https://github.com/zeromq/pyzmq)).

## What are agents?

Agent programming is based on the idea of autonomous _agents_ interacting with each other in order to perform tasks.
Such an agent is provided with inputs from the 'environment', which are often called _percepts_ (i.e. perceptual, or sensory information), and produces outputs which are called _actions_: procedures that effect the environment in some way. This creates a kind of feedback loop, an example of which is shown in the picture below:

![A simple reflex agent architecture.](https://upload.wikimedia.org/wikipedia/commons/3/3f/IntelligentAgent-SimpleReflex.png)  
_From [Wikipedia](https://en.wikipedia.org/wiki/Intelligent_agent)._

Such an agent is often described as a function _f_, taking a sequence of percepts (_P*_) to an action (_A_):

<img src="https://render.githubusercontent.com/render/math?math=f%20%3A%20P%5E*%20%5Crightarrow%20A">

However, a more appropriate description of an agent in Ajay is a function _g_ which takes a sequence of percepts (_P*_) to a sequence of actions (_A*_):

<img src="https://render.githubusercontent.com/render/math?math=g%20%3A%20P%5E*%20%5Crightarrow%20A%5E*">

To read some more about agent programming in general, see the paper by Shoham (1993) in the repository, or [the book by Russell and Norvig](http://aima.cs.berkeley.edu).

## Agents in Ajay

These ideas about agents are implemented in Ajay: an agent is a function which takes in percepts and produces actions. The library defines which percepts and actions exist, runs the agent function, provides it with percepts, and execute the actions that it performs. A simple agent might look like this:
```python
async def bounce(percepts, act):
    await print("Started agent.")

    await print("Waiting for messages...")
    async for msg in percepts:
        if isinstance(msg, MessagePercept):
            await print(f"Received message: {msg.content}")
            await print(f"Sending contents back to {msg.sender}")
            await send(msg.sender, msg.content)
```
Two kinds of actions are performed here: `print` (which prints to the console with some extra info) and `send` (which sends a message to another agent). These actions look like regular functions here, but they actually push an `[...]Action` object into a stream internally, so the agent is really transforming a sequence of percepts into a sequence of action objects. As you can see, all library code is asynchronous: each action is prefaced by await, and the loop over the percepts is an `async for`. The only kind of percepts that this agent deals with are messages (`MessagePercept`s), and when it receives a message it just echoes it back to the sender.

 > Note that the normal print function is shadowed here: this is of course very edgy and not required ;)
 > Instead of `print(x)` you can also do `act(Print(x))` or `act(PrintAction(x))`, depending on the level of verbosity you want.

## Dealing with IO

When strictly following this paradigm, _all_ interaction with the 'outside world' should go through this mechanism of percepts and actions. This also applies to things like local file IO. The reason is that we would like to stick to this idea of an agent being a deterministic function from percepts to actions: if we take an action based on the contents of a file, the function becomes unpredictable. The solution is to make the file contents into one of the percepts as well. To accomplish this, the `act` function can be used to perform built-in actions, but it can also be used to transform any `async` function call into an action, and then provide its result as a percept. For an example, see `tests/test_agent_fileio.py`.

The main advantage of such an approach is _reproducibility_. In some sense, the observable behavior of an agent is entirely determined by the actions it performs, and so can be rigorously studied and even executed in a different context than the one in which the agent originally ran. Moreover, the actions the agent produces are in turn entirely determined by the percepts that it receives. That means if one has a record of the percepts, one can 'replay' an agent's execution in a sandbox state, where it will produce the same actions but these actions do not have to affect the environment. For an example of this, see `tests/test_agent_message.py`.

## Agent communication

The agents commuincate with each other via _message passing_. Currently, no special constraints are placed on these messages, but there is actually a base on which these messages can be built, the [FIPA-ACL](http://www.fipa.org/specs/fipa00061/SC00061G.html) (Agent Communication Language) standard, which is in turn based on the theory of [speech acts](https://en.wikipedia.org/wiki/Speech_act). Other Python libraries have the ability to produce messages confirming to this specification, and it is also a goal to include a (simple) implementation of it here.

These ACL messages provide one with a lot of metadata, but content-wise they are actually quite flexible. That is because for any application, the relevant terms one may use to describe the things the agents need to communicate will differ. Here is where the concept of _ontology_ comes in: an ontology is a structure which defines a set of terms, their properties and their relationships to each other. Basically, it is a way for agents to construct a shared basis so they both know what they are talking about. There are also standards for constructing these ontologies, such as [OWL](https://en.wikipedia.org/wiki/Web_Ontology_Language). OWL ontologies are heavily based on mathematical logic: generally, an OWL ontology is just a collection of propositions (or facts) about a set of terms. This is somewhat similar to an object hierarchy (e.g. a proposition might be "a Car is a Vehicle"), but with some important differences. The most important is the possibility for automated _reasoning_, where the facts in the ontology can be logically combined to produce new facts. (I believe there may be a link here to the reactive programming paradigm as in [MobX](https://mobx.js.org).)

 > Currently, there is no support for specific types of messages, nor integration with any kind of ontologies, but these are interesting possibilities for the future.
 > However, the aim is also to make all of these features optional: if you just want a function which runs continously and use your own methods for state management and communication, that's fine too. No need to adjust all your logic to awkwardly use our preferred data structures if you don't want to ;)

### To-do list

Things which I would like to work on next:

 - Translating/designing more/better examples of agent programming which could be done with this framework. Both for illustration of use cases and inspiration for further developments.
 - More comments and (API) documentation ;)
 - Support for constructing and processing ACL messages easily
 - Run tests in virtual time (inspiration from aioreactive)
 - Think about a natural form of state management. Probably using some kind of ontology, but how to design an interface which works well in the paradigm?

