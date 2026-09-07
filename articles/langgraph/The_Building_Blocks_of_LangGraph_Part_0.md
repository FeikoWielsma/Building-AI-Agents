# The Building Blocks of LangGraph (Part 0)

**Bessie Delight Kekeli** · 11 min read · Jun 3, 2026

*For other parts of the series:* [Part 0](https://medium.com/@bessiedelight/the-building-blocks-of-langgraph-1975904edac8) , [Part 1](https://medium.com/towards-artificial-intelligence/the-langgraph-mental-model-a-standardized-architecture-guide-for-every-agent-youll-ever-build-d02265f3bebf) , [Part 2](https://medium.com/@bessiedelight/langgraph-memory-the-complete-practical-guide-to-managing-what-your-agent-remembers-d865d505a59e) , [Part 3](https://medium.com/@bessiedelight/langgraph-human-in-the-loop-pausing-reviewing-and-rewinding-your-agent-4028bd05b049)

<!-- IMAGE 1: article lead image, sourced from the post's social-preview (og:image) URL. -->
![Figure 1](https://miro.medium.com/v2/resize:fit:720/format:webp/1*Q5UozakGUGtRpzd2jPVHpA.png)

As Large Language Models (LLMs) have become more capable, developers have moved beyond simple chatbots and begun building systems that can reason, make decisions, use tools, retrieve information, interact with APIs, and collaborate with other AI agents.

Building these systems introduces a new challenge:

How do we coordinate and manage the flow of intelligence?

This is the problem that LangGraph was created to solve.

At its core, LangGraph is a framework for building stateful, controllable, and production-ready AI workflows. It allows developers to define how AI agents think, make decisions, communicate with tools, and move through complex tasks.

If LangChain helps you connect AI components together, LangGraph helps you orchestrate how those components behave over time.

LangGraph is an orchestration framework built by the team behind LangChain.

It allows developers to model AI applications as a graph

## The Simplest Graph(agent flow)

Let's build a simple graph with 3 nodes and one conditional edge.

<!-- IMAGE 2: original image source: Medium CDN (miro.medium.com). -->
![Figure 2](https://miro.medium.com/v2/resize:fit:720/format:webp/0*zl_Yu3xNMckbUkxW.png)

The easiest way to understand nodes, edges, and state is to imagine a food delivery process.

A node is simply a task or action that does something.

For example:

**Receive Order** is a node.

**Prepare Food** is another node.

**Deliver Food** is another node.

Every time some work is performed, you are at a node.

An edge is the path that tells the system where to go next.

For example:

```
Receive Order
      ↓
Prepare Food
      ↓
Deliver Food
```

Those arrows are the edges.

The edge is not doing any work itself. It simply says:

"After this step finishes, go to that step."

Think of an edge as a road connecting two cities. The cities are the nodes, and the road is the edge.

A state is the information that travels through the entire process.

Imagine a customer orders:

```
Pizza
Address: 123 Main Street
Customer: John
```

When the order is received, that information enters the system.

As the order moves from:

```
Receive Order
      ↓
Prepare Food
      ↓
Deliver Food
```

the information moves along with it.

That information is the state.

## Let's build our first simple agent

<!-- IMAGE 3: original image source: Medium CDN (miro.medium.com). -->
![Figure 3](https://miro.medium.com/v2/resize:fit:720/format:webp/0*zl_Yu3xNMckbUkxW.png)

### State

Think of state as the graph's shared memory.

It is the information that travels through the workflow as it moves from one node to another. Every node can read the state, update it, and pass the updated version to the next node.

In this example, the state contains a single piece of information called graph_state. First, define the State of the graph.

The State schema serves as the input schema for all Nodes and Edges in the graph.

Let's use the TypedDict class from python's typing module as our schema, which provides type hints for the keys.

```python
from typing_extensions import TypedDict

class State(TypedDict):
    graph_state: str
```

### Nodes

A node is simply a function that performs some work.

When a node runs, it receives the current state, does something with it, and returns an updated state.

You can think of a node as a worker in a factory. The worker receives a package (the state), modifies it, and then passes it along.

The first positional argument is the state, as defined above.

Because the state is a TypedDict with schema as defined above, each node can access the key, graph_state, with state['graph_state'].

Each node returns a new value of the state key graph_state.

By default, the new value returned by each node will override the prior state value.

```python
def node_1(state):
  print("---Node 1---")
  return {"graph_state": state['graph_state'] + "I am"}

def node_2(state):
  print("---Node 2---")
  return {"graph_state": state['graph_state'] + "happy!"}

def node_3(state):
  print("---Node 3---")
  return {"graph_state": state['graph_state'] + "sad!"}
```

### Edges

An edge is simply a connection between nodes. It tells the graph where to go after a node finishes its work.

A normal edge is a fixed path. After one node completes, the graph always moves to the same next node.

For example, if a workflow has "Collect Data" followed by "Analyze Data," the graph will always move from the first node to the second.

A conditional edge is a decision point. Instead of always following the same path, the graph looks at the current state and decides where to go next.

For example, after analyzing data, the graph might ask:

"Do I have enough information?"

If the answer is yes, it moves to "Generate Report."

If the answer is no, it moves back to "Collect More Data."

Conditional edges are implemented as functions that return the next node to visit based on some logic.

```python
import random
from typing import Literal

def decide_mood(state) -> Literal["node_2", "node_3"]:
  
  # Often, we will use state to decide on the next node to visit
  user_input = state['graph_state']

    
  # Here, let's just do a 50 / 50 split between nodes 2, 3
  if random.random() < 0.5

      # 50% of the time, we return Node 2
      return "node_2" 
  
  # 50% of the time, we return Node 3
  return "node_3"
```

### Graph Construction

Now, we build the graph from our components defined above.

The StateGraph class is the graph class that we can use.

First, we initialize a StateGraph with the State class we defined above.

Then, we add our nodes and edges.

We use the START Node, a special node that sends user input to the graph, to indicate where to start our graph.

The END Node is a special node that represents a terminal node.

Finally, we compile our graph to perform a few basic checks on the graph structure.

We can visualize the graph as a Mermaid diagram.

```python
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

#Build Graph
builder = StateGraph(state)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

#Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

#Add
graph = builder.compile()

#View
display(Image(graph.get_graph().draw_mermaid_png()))
#OUTPUT
```

<!-- IMAGE 4: original image (Mermaid graph output) source: Medium CDN (miro.medium.com). -->
![Figure 4](https://miro.medium.com/v2/resize:fit:720/format:webp/1*xQAUYUG-phm_3TIYbZK2rw.png)

### Graph Invocation

The compiled graph implements the runnable protocol.

This provides a standard way to execute LangChain components.

invoke is one of the standard methods in this interface.

The input is a dictionary {"graph_state": "Hi, this is lance."}, which sets the initial value for our graph state dict.

When invoke is called, the graph starts execution from the START node.

It progresses through the defined nodes (node_1, node_2, node_3) in order.

The conditional edge will traverse from node 1 to node 2 or 3 using a 50/50 decision rule.

Each node function receives the current state and returns a new value, which overrides the graph state.

The execution continues until it reaches the END node.

```python
graph.invoke({"graph_state" : "Hi, this is Lance."})
###OUTPUT
---Node 1---
---Node 3---
{'graph_state': 'Hi, this is Lance. I am sad!'}
```

invoke runs the entire graph synchronously.

This waits for each step to complete before moving to the next.

It returns the final state of the graph after all nodes have executed.

In this case, it returns the state after node_3 has completed:

```
{'graph_state': 'Hi, this is Lance. I am sad!'}
```

## Chain

We built a simple graph with nodes, normal edges, and conditional edges.

Now, let's build up to a simple chain that combines 4 concepts.

- Using chat messages as our graph state
- Using chat models in graph nodes
- Binding tools to our chat model
- Executing tool calls in graph nodes

<!-- IMAGE 5: original image source: Medium CDN (miro.medium.com). -->
![Figure 5](https://miro.medium.com/v2/resize:fit:720/format:webp/1*cfN6fX7jy8MUBRIr3kqR9w.png)

```
%%capture --no-stderr
%pip install --quiet -U langchain_openai langchain_core langgraph
```

### Messages

Chat models can use messages, which capture different roles within a conversation.

LangChain supports various message types, including HumanMessage, AIMessage, SystemMessage, and ToolMessage.

These represent a message from the user, from chat model, for the chat model to instruct behavior, and from a tool call.

Let's create a list of messages.

Each message can be supplied with a few things:

- content - content of the message
- name - optionally, a message author
- response_metadata - optionally, a dict of metadata (e.g., often populated by model provider for AIMessages)

```python
from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage

messages = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]
messages.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))
messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))

for m in messages:
    m.pretty_print()
#OUTPUT
================================== Ai Message ==================================
Name: Model

So you said you were researching ocean mammals?
================================ Human Message =================================
Name: Lance

Yes, that's right.
================================== Ai Message ==================================
Name: Model

Great, what would you like to learn about.
================================ Human Message =================================
Name: Lance

I want to learn about the best place to see Orcas in the US.
```

### Chat Models

Chat models use a sequence of messages as input and support message types, as discussed above.

There are many to choose from! Let's work with OpenAI.

We can load a chat model and invoke it with out list of messages.

We can see that the result is an AIMessage with specific response_metadata.

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")
result = llm.invoke(messages)
type(result)
result
#OUTPUT

langchain_core.messages.ai.AIMessage
```

```python
result
AIMessage(content='One of the best places to see orcas in the United States is the Pacific Northwest, particularly around the San Juan Islands in Washington State. Here are some details:\n\n1. **San Juan Islands, Washington**: These islands are a renowned spot for whale watching, with orcas frequently spotted between late spring and early fall. The waters around the San Juan Islands are home to both resident and transient orca pods, making it an excellent location for sightings.\n\n2. **Puget Sound, Washington**: This area, including places like Seattle and the surrounding waters, offers additional opportunities to see orcas, particularly the Southern Resident killer whale population.\n\n3. **Olympic National Park, Washington**: The coastal areas of the park provide a stunning backdrop for spotting orcas, especially during their migration periods.\n\nWhen planning a trip for whale watching, consider peak seasons for orca activity and book tours with reputable operators who adhere to responsible wildlife viewing practices. Additionally, land-based spots like Lime Kiln Point State Park, also known as "Whale Watch Park," on San Juan Island, offer great opportunities for orca watching from shore.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 228, 'prompt_tokens': 67, 'total_tokens': 295, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-2024-08-06', 'system_fingerprint': 'fp_50cad350e4', 'finish_reason': 'stop', 'logprobs': None}, id='run-57ed2891-c426-4452-b44b-15d0a5c3f225-0', usage_metadata={'input_tokens': 67, 'output_tokens': 228, 'total_tokens': 295, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})
```

### Tools

Tools are useful whenever you want a model to interact with external systems.

External systems (e.g., APIs) often require a particular input schema or payload, rather than natural language.

When we bind an API, for example, as a tool we given the model awareness of the required input schema.

The model will choose to call a tool based upon the natural language input from the user.

And, it will return an output that adheres to the tool's schema.

Many LLM providers support tool calling and tool calling interface in LangChain is simple.

You can simply pass any Python function into ChatModel.bind_tools(function).

<!-- IMAGE 6: original image source: Medium CDN (miro.medium.com). -->
![Figure 6](https://miro.medium.com/v2/resize:fit:720/format:webp/1*go1-UAvi9Ex2eRwvJBgRDg.png)

Let's showcase a simple example of tool calling!

The multiply function is our tool.

```python
def multiply(a:int, b:int)-> int:
  return a*b

llm_with_tools = llm.bind_tools([multiply])
```

If we pass an input — e.g., "What is 2 multiplied by 3" - we see a tool call returned.

The tool call has specific arguments that match the input schema of our function along with the name of the function to call. {'arguments': '{"a":2,"b":3}', 'name': 'multiply'}

```python
tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 multiplied by 3
", name="Lance")])
tool_call.tool_calls
#OUTPUT
[{'name': 'multiply',
  'args': {'a': 2, 'b': 3},
  'id': 'call_lBBBNo5oYpHGRqwxNaNRbsiT',
  'type': 'tool_call'}]
```

### Using messages as state

With these foundations in place, we can now use messages in our graph state.

Let's define our state, MessagesState, as a TypedDict with a single key: messages.

messages is simply a list of messages, as we defined above (e.g., HumanMessage, etc).

```python
from typing_extentions import TypedDict
from langchain_core.messges import AnyMessage

class MessagesState(TypedDict):
  messages : list[AnyMessage]
```

### Reducers

Now, we have a minor problem!

As we discussed, each node will return a new value for our state key messages.

But, this new value will overwrite the prior messages value!

As our graph runs, we want to append messages to our messages state key.

We can use reducer functions to address this.

Reducers specify how state updates are performed.

If no reducer function is specified, then it is assumed that updates to the key should override it as we saw before.

But, to append messages, we can use the pre-built add_messages reducer.

This ensures that any messages are appended to the existing list of messages.

We simply need to annotate our messages key with the add_messages reducer function as metadata.

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

Since having a list of messages in graph state is so common, LangGraph has a pre-built MessagesState!

MessagesState is defined:

- With a pre-build single messages key
- This is a list of AnyMessage objects
- It uses the add_messages reducer

We'll usually use MessagesState because it is less verbose than defining a custom TypedDict, as shown above.

```python
from langgraph.graph import MessagesState

class MessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built 
    pass
```

To go a bit deeper, we can see how the `add_messages` reducer works in isolation.

```python
# Initial state
initial_messages = [AIMessage(content="Hello! How can I assist you?", name="Model"),
                    HumanMessage(content="I'm looking for information on marine biology.", name="Lance")
                   ]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model")

# Test
add_messages(initial_messages , new_message)
```

### Our graph

Now, lets use MessagesState with a graph.

```python
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
    
# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# View
display(Image(graph.get_graph().draw_mermaid_png()))
#OUTPUT
```

<!-- IMAGE 7: original image (Mermaid graph output) source: Medium CDN (miro.medium.com). -->
![Figure 7](https://miro.medium.com/v2/resize:fit:720/format:webp/1*ZuAHh0uzmjFHrw-OhRtwZw.png)

If we pass in `Hello!`, the LLM responds without any tool calls.

```python
messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
for m in messages['messages']:
    m.pretty_print()
#OUTPUT
================================ Human Message =================================

Hello!
================================== Ai Message ==================================

Hi there! How can I assist you today?
```

The LLM chooses to use a tool when it determines that the input or task requires the functionality provided by that tool.

```python
messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
for m in messages['messages']:
    m.pretty_print()
OUTPUT

================================ Human Message =================================

Multiply 2 and 3!
================================== Ai Message ==================================
Tool Calls:
  multiply (call_Er4gChFoSGzU7lsuaGzfSGTQ)
 Call ID: call_Er4gChFoSGzU7lsuaGzfSGTQ
  Args:
    a: 2
    b: 3
```

GREAT JOB GUYS ! 🚀

---

**Tags:** Langgraph · Langchain · AI Agent · AI · LLM

*Written by Bessie Delight Kekeli — AI engineer by day, writer by night. Turning cutting-edge tech into articles anyone can understand.*
