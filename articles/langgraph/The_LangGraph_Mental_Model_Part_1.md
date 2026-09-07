# The LangGraph Mental Model: A standardized architecture guide for every agent you'll ever build

**Bessie Delight Kekeli** · 20 min read · Jun 5, 2026

<!-- IMAGE 1 (lead image): source: Medium CDN (miro.medium.com). -->
![Figure 1](https://miro.medium.com/v2/resize:fit:720/format:webp/1*oIVe6tO7VPVWwUdwZyPZcA.png)

*Part 1 : A structured, module-by-module reference for developers who understand the concept but want to finally internalize the code*

*For other parts of the series:* [Part 0](https://medium.com/@bessiedelight/the-building-blocks-of-langgraph-1975904edac8) , [Part 1](https://medium.com/towards-artificial-intelligence/the-langgraph-mental-model-a-standardized-architecture-guide-for-every-agent-youll-ever-build-d02265f3bebf) , [Part 2](https://medium.com/@bessiedelight/langgraph-memory-the-complete-practical-guide-to-managing-what-your-agent-remembers-d865d505a59e) , [Part 3](https://medium.com/@bessiedelight/langgraph-human-in-the-loop-pausing-reviewing-and-rewinding-your-agent-4028bd05b049)

> **Who this is for:** You've watched the videos. You've read the docs. You understand what a graph is, what a node does, what an edge decides. But the moment you open a blank file, you freeze. This article is the bridge between understanding LangGraph and writing it fluently.

## Introduction: Why LangGraph Code Feels Hard Even When the Concept Doesn't

There is a specific kind of frustration that comes with LangGraph development. The mental model is elegant — you have a graph, nodes do work, edges make decisions, state carries memory. It makes sense. You could draw it on a whiteboard in five minutes.

Then you open your editor, and suddenly there are imports you can't remember, classes you can't place, function signatures you can't recall, and five different ways the same thing could be written. The concept is clear. The code is a fog.

The root cause is that LangGraph code has no enforced structure. The library gives you powerful primitives, but it doesn't tell you how to organize them. Every tutorial and GitHub repo arranges things differently. So your brain never gets a stable scaffold to hold onto.

This article solves that. We are going to define one canonical, standardized way to structure every LangGraph agent you will ever build — from a simple single-agent chatbot to a complex multi-agent pipeline. Like the memory diagram in LangGraph that shows you what your agent has done, this article gives you the equivalent for code: a reliable structure you can memorize, recall, and reach for every single time.

We call this structure the SIDE framework: State → Instructions → Decisions → Execution. Everything in a LangGraph application falls into one of these four modules.

## The Big Picture: Four Modules, One File Order

Before we go deep, here is the 30,000-foot view. Every LangGraph application you write should follow this module order from top to bottom:

```
langgraph_agent.py
│
├── MODULE 1: IMPORTS & CONFIGURATION
│   └── All your libraries, API keys, model setup
│
├── MODULE 2: STATE
│   └── The TypedDict that defines your agent's memory
│
├── MODULE 3: TOOLS (optional, but common)
│   └── Functions decorated with @tool that the LLM can call
│
├── MODULE 4: NODES
│   └── Functions that do the actual work at each graph step
│
├── MODULE 5: EDGES & ROUTING
│   └── Functions that decide what happens next
│
├── MODULE 6: GRAPH ASSEMBLY
│   └── Where you build, wire, and compile the graph
│
└── MODULE 7: ENTRYPOINT
    └── The __main__ block or invoke() call that runs everything
```

This is your canonical skeleton. Memorize this order. Every time you start a new LangGraph project, you open a file and write these seven section headers as comments. Then you fill them in. Let's build each one from the ground up.

## Module 1: Imports & Configuration

<!-- IMAGE 2: source: Medium CDN (miro.medium.com). -->
![Figure 2](https://miro.medium.com/v2/resize:fit:720/format:webp/1*ZNX3IXDEuqJWzpJuDKOpeg.png)

### The Concept

This module is your toolbox setup. Before a carpenter starts building, they lay all their tools on the bench. This module does the same — it tells Python what external capabilities you're bringing in, and it configures the AI model you'll be working with.

### The Keywords You Need to Know

- **`ChatOpenAI` / `ChatAnthropic`** — the LLM class. This is your language model, the brain. You instantiate it here once and reference it everywhere else.
- **`StateGraph`** — the core LangGraph class. This is the graph builder. Think of it as the blueprint paper you draw your graph on.
- **`END`** — a special LangGraph constant that represents the terminal node. When an edge points to END, the graph stops.
- **`MemorySaver`** — a checkpointer class that gives your graph persistent memory across multiple conversation turns.

### The Standard Template

```python
# --- Standard Library ---
import os
from typing import TypedDict, Annotated, Literal
# --- LangChain Core ---
from langchain_openai import ChatOpenAI          # or ChatAnthropic, ChatGroq, etc.
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
# --- LangGraph Core ---
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages  # The message reducer
from langgraph.prebuilt import ToolNode            # Pre-built node for tool execution
from langgraph.checkpoint.memory import MemorySaver
# --- Configuration ---
# Always name your model variable 'llm' - it's the standard in every node
llm = ChatOpenAI(
    model="gpt-4o",         # or "claude-3-5-sonnet-20241022", etc.
    temperature=0,          # 0 = deterministic; raise for creativity
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

### Why This Exact Structure

Notice that imports are grouped into four logical clusters: standard library, LangChain (the LLM layer), LangGraph (the graph layer), and configuration. This mirrors how LangGraph itself is layered — LangChain handles the AI primitives, LangGraph handles the orchestration. Keeping them visually separated helps you instantly find what belongs where when debugging.

The single most important habit here is naming your model `llm`. Every node function you write later will reference this variable. If you call it `model` in one project and `chat` in another, your code becomes inconsistent and harder to scan.

## Module 2: State

<!-- IMAGE 3: source: Medium CDN (miro.medium.com). -->
![Figure 3](https://miro.medium.com/v2/resize:fit:720/format:webp/1*AAaPz9s8sXcMQr_zcHYoMw.png)

### The Concept

State is your agent's working memory. It is the single source of truth that travels through the entire graph. Every node reads from it, every node can write to it, and the graph engine manages its lifecycle. Understanding State deeply is arguably the most important thing in LangGraph.

Think of it like a whiteboard in a team meeting room. Every person who walks in (every node) can read what's on the board and add to it. The board persists across the whole meeting (the whole graph run).

### The Keywords You Need to Know

- **`TypedDict`** — a Python class that defines the shape of your state. It's like a schema. You inherit from it to create your State class.
- **`Annotated`** — a Python type hint wrapper. In LangGraph, you use it to attach a reducer to a field. A reducer is a function that controls how new values merge with existing values in the state.
- **`add_messages`** — the built-in LangGraph reducer for the messages field. Instead of replacing the messages list every time a node adds a message, add_messages appends the new messages to the existing list. This is the most commonly used reducer.
- **`operator.add`** — another common reducer for fields that should accumulate by addition (like a list of results or a counter).

### The Standard Template

```python
# ============================================================
# MODULE 2: STATE
# ============================================================
class AgentState(TypedDict):
    # 'messages' is the heartbeat of almost every LangGraph agent.
    # Annotated[list, add_messages] means: "this is a list, and when 
    # a node writes to it, append - don't replace."
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Add custom fields below for your specific agent's needs.
    # Fields without a reducer are REPLACED each time a node writes to them.
    
    # Example: a simple string field (gets replaced each write)
    current_task: str
    
    # Example: a list you want to accumulate (use operator.add as reducer)
    # results: Annotated[list[str], operator.add]
    
    # Example: a counter
    # iteration_count: int
```

### The Reducer Mental Model

This is the point where most beginners get confused. Let's clear it up permanently with a concrete analogy.

Imagine your State is a form being passed around an office. The messages field on that form works like a sticky note pad — every person who touches the form adds a new sticky note. They never erase the old ones. That's add_messages.

A field without a reducer is like a single text box on that form. Each person who fills it in overwrites what the previous person wrote. That's the default LangGraph behavior: last write wins.

The rule of thumb is simple: use `Annotated[list, add_messages]` for your messages field always, and use `Annotated[list, operator.add]` for any other list you want to grow. Leave everything else without a reducer.

## Module 3: Tools

<!-- IMAGE 4: source: Medium CDN (miro.medium.com). -->
![Figure 4](https://miro.medium.com/v2/resize:fit:720/format:webp/1*qwSB7Lf286_gnwO0BNJQXw.png)

### The Concept

Tools are the hands of your agent. Your LLM is the brain — it reasons and decides. But it cannot actually do anything in the world by itself. Tools give it the ability to search the web, call an API, run code, query a database, or execute any Python function you define.

This module is optional. If your agent only generates text and doesn't need to interact with external systems, you can skip it. But most real-world agents need tools.

### The Keywords You Need to Know

- **`@tool`** — a decorator from LangChain that transforms a regular Python function into a LangGraph-compatible tool. The function's docstring becomes the tool's description that the LLM reads to decide whether to use it.
- **`ToolNode`** — a pre-built LangGraph node (from langgraph.prebuilt) that automatically executes whatever tools the LLM decided to call. This saves you from writing the tool-execution logic yourself.
- **`bind_tools`** — a method you call on your LLM instance to attach tools to it. After binding, the LLM knows which tools exist and can choose to invoke them by generating a special tool_calls message instead of regular text.

### The Standard Template

```python
# ============================================================
# MODULE 3: TOOLS
# ============================================================
@tool
def search_web(query: str) -> str:
    """Search the web for current information about a topic.
    
    Use this when you need real-time information that is not in 
    your training data, such as recent news or live prices.
    
    Args:
        query: The search query string.
    
    Returns:
        A string containing search results.
    """
    # Your actual implementation here (e.g., Tavily, SerpAPI, etc.)
    # Placeholder for illustration:
    return f"Search results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.
    
    Use this for any arithmetic, algebra, or numerical computation.
    
    Args:
        expression: A valid Python math expression as a string, e.g. '2 + 2 * 10'
    
    Returns:
        The computed result as a string.
    """
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# Collect all tools into a list - this is the pattern you always follow
tools = [search_web, calculate]
# Bind tools to the LLM so it knows they exist and can choose to call them
llm_with_tools = llm.bind_tools(tools)
# Create the pre-built ToolNode that will execute tool calls automatically
tool_node = ToolNode(tools)
```

### The Tool Docstring is Critical

This is one of the most important things beginners miss: the LLM uses your tool's docstring to decide whether to use that tool. It literally reads the text you write in the triple quotes. A vague or missing docstring means the LLM won't know when to reach for your tool. Always write clear, specific docstrings that describe what the tool does and when to use it.

## Module 4: Nodes

<!-- IMAGE 5: source: Medium CDN (miro.medium.com). -->
![Figure 5](https://miro.medium.com/v2/resize:fit:720/format:webp/1*UtzJI9qCX2IaTUO8thqAew.png)

### The Concept

Nodes are the workers of your graph. Each node is a Python function that receives the current State, does some work — calls an LLM, processes data, calls a tool — and returns a dictionary of updates to the State. That's it. That's the entire job of a node.

Nodes never control what happens next. They just do their work and update the state. The routing (what runs after this node) is handled entirely in Module 5.

### The Keywords You Need to Know

- **`state`** — the parameter every node function receives. It is a dictionary matching the shape of your AgentState. Inside the node, you access it like state["messages"] or state["current_task"].
- **`HumanMessage`, `AIMessage`, `SystemMessage`** — the three message types you will use constantly. HumanMessage is what the user said. AIMessage is what the LLM responded. SystemMessage is your instructions to the LLM (system prompt).
- **`invoke`** — the method you call on the LLM (or llm_with_tools) to get a response. You pass it a list of messages, and it returns an AIMessage.
- **Return value** — every node returns a dictionary whose keys match the field names in AgentState. The values in this dictionary are updates to the state, not the full state. LangGraph merges them using the reducers you defined.

### The Standard Template

```python
# ============================================================
# MODULE 4: NODES
# ============================================================
# ── Node: Agent (the reasoning brain) ───────────────────────
def agent_node(state: AgentState) -> dict:
    """The central reasoning node. Calls the LLM and decides 
    whether to respond or call a tool."""
    
    # Build the message list to send to the LLM.
    # Always include a system message to set behavior.
    system_prompt = SystemMessage(content=(
        "You are a helpful assistant. Use the available tools "
        "when you need real-time information or computation. "
        "Respond clearly and concisely."
    ))
    
    # The LLM receives the system prompt + all previous messages in state
    messages_to_send = [system_prompt] + state["messages"]
    
    # Call the LLM. Use llm_with_tools if you have tools; plain llm if not.
    response = llm_with_tools.invoke(messages_to_send)
    
    # Return the LLM's response as a state update.
    # add_messages will APPEND this AIMessage to state["messages"].
    return {"messages": [response]}

# ── Node: Summarizer (example of a non-LLM processing node) ─
def summarize_node(state: AgentState) -> dict:
    """Summarizes the conversation so far to keep context short.
    This shows that nodes don't have to call an LLM - they can 
    do any Python processing."""
    
    all_messages = state["messages"]
    
    # Summarize with the LLM (a different prompt, same LLM)
    summary_prompt = [
        SystemMessage(content="Summarize the following conversation in 2-3 sentences."),
        HumanMessage(content=str(all_messages))
    ]
    
    summary_response = llm.invoke(summary_prompt)
    
    # Replace messages with a fresh start containing just the summary
    return {
        "messages": [AIMessage(content=f"[Summary] {summary_response.content}")]
    }
```

### The Node Mental Model

Here is a mental image that makes nodes click: think of a node as a relay baton runner. They receive the baton (state), run their leg of the race (do their work), and hand the baton off (return updated state). They don't decide who runs next — that's the race director's job (the edges). They just run.

Every node function signature is always: `def my_node(state: AgentState) -> dict`. The input is always the full state. The output is always a dictionary of the fields you want to update.

## Module 5: Edges & Routing

<!-- IMAGE 6: source: Medium CDN (miro.medium.com). -->
![Figure 6](https://miro.medium.com/v2/resize:fit:720/format:webp/1*1ivibtWIuuVpH5uUcQRCGw.png)

### The Concept

Edges are the decision logic of your graph. They connect nodes to each other and determine the flow of execution. In LangGraph, there are two kinds of edges:

Static edges connect one node to another unconditionally. "After the summarizer runs, always go to the agent." No decision involved — just a direct wire.

Conditional edges inspect the state and return a string indicating which node to go to next. This is where your agent's intelligence about its own flow lives. Should we call a tool? Should we end? Should we loop back and try again?

### The Keywords You Need to Know

- **`add_edge(A, B)`** — adds a static edge from node A to node B. A always leads to B.
- **`add_conditional_edges(source, routing_function, mapping)`** — adds a conditional edge from source. The routing_function is called with the current state and returns a string. The mapping dictionary translates that string into the actual next node name.
- **`tools_condition`** — a pre-built LangGraph routing function (from langgraph.prebuilt) that inspects the last message in state and checks if the LLM made any tool calls. If it did, it routes to "tools". If it didn't, it routes to END. This is the standard pattern for tool-using agents and you should memorize it.
- **`START`** — a LangGraph constant that represents the beginning of the graph. When you set the entry point, you're adding an edge from START to your first node.

### The Standard Template

```python
# ============================================================
# MODULE 5: EDGES & ROUTING
# ============================================================
# Import the pre-built tool routing function
from langgraph.prebuilt import tools_condition
# ── Custom Routing Function Example ─────────────────────────
def should_continue(state: AgentState) -> Literal["tools", "summarize", "__end__"]:
    """Custom router for the agent node.
    
    Routing functions always:
    1. Receive the current state as input
    2. Return a string that maps to the next node (or END)
    
    The return values must match the keys in add_conditional_edges' mapping.
    """
    
    last_message = state["messages"][-1]  # Look at what the LLM just said
    
    # Case 1: The LLM decided to call a tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Case 2: The conversation is getting long - summarize before continuing
    if len(state["messages"]) > 20:
        return "summarize"
    
    # Case 3: The LLM gave a direct answer - we're done
    return "__end__"  # LangGraph's internal name for END
```

### The Routing Mental Model

Think of a routing function as a train switchboard operator. The train (execution) arrives at a station (a node completes), and the operator looks at the train's manifest (the current state) and flips the right switch to send the train down the correct track. The operator doesn't move the train — they just decide the direction. LangGraph moves the train.

One critical rule to internalize: routing functions never modify state. They only read it. Any modification to state happens in nodes only. If you find yourself wanting to update state inside a routing function, move that logic into a node.

## Module 6: Graph Assembly

<!-- IMAGE 7: source: Medium CDN (miro.medium.com). -->
![Figure 7](https://miro.medium.com/v2/resize:fit:720/format:webp/1*u2h5fNbt9eayNxR-7h45ow.png)

### The Concept

This is where everything comes together. Think of this module as construction day. Modules 1–5 were preparation — defining materials, cutting pieces, laying them out. Module 6 is where you actually build the structure by wiring everything together and compiling it.

The graph assembly follows a strict, always-identical five-step sequence that you should commit to memory: Initialize → Register Nodes → Set Entry → Wire Edges → Compile.

### The Keywords You Need to Know

- **`StateGraph(AgentState)`** — instantiates the graph builder using your State class as the schema. Every node in the graph must return updates compatible with this schema.
- **`add_node(name, function)`** — registers a node in the graph. The name is the string identifier you'll use in edges. The function is the node function from Module 4.
- **`set_entry_point(name)`** — declares which node runs first when you invoke the graph.
- **`add_edge(A, B)`** — wires a direct, unconditional connection from node A to node B.
- **`add_conditional_edges(source, router, mapping)`** — wires a conditional branch from the source node, using your routing function, with a mapping from return strings to destination node names.
- **`compile(checkpointer=...)`** — seals the graph into a runnable object (a CompiledGraph). After this, you cannot add more nodes or edges. The optional checkpointer argument enables persistent memory.

### The Standard Template

```python
# ============================================================
# MODULE 6: GRAPH ASSEMBLY
# ============================================================
# ── Step 1: Initialize ──────────────────────────────────────
# Always pass your State class to StateGraph
graph_builder = StateGraph(AgentState)
# ── Step 2: Register All Nodes ──────────────────────────────
# Format: add_node("node_name_as_string", node_function)
# The string name is what you use in ALL edge definitions
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)      # The pre-built ToolNode from Module 3
graph_builder.add_node("summarize", summarize_node)
# ── Step 3: Set Entry Point ─────────────────────────────────
# Which node runs first when we invoke the graph?
graph_builder.set_entry_point("agent")
# ── Step 4: Wire the Edges ──────────────────────────────────
# Conditional edge from agent: check if we need tools, a summary, or we're done
graph_builder.add_conditional_edges(
    "agent",          # Source node
    should_continue,  # Routing function from Module 5
    {
        "tools": "tools",           # If router returns "tools" → go to tools node
        "summarize": "summarize",   # If router returns "summarize" → go to summarize node
        "__end__": END,             # If router returns "__end__" → stop the graph
    }
)
# Static edge: after tools run, always go back to agent (the ReAct loop)
graph_builder.add_edge("tools", "agent")
# Static edge: after summarization, always return to agent
graph_builder.add_edge("summarize", "agent")
# ── Step 5: Compile ─────────────────────────────────────────
# Without checkpointer: no persistent memory (stateless per invocation)
# With checkpointer: memory persists across turns (stateful conversations)
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

### The Assembly Mental Model

The clearest way to picture this is with a circuit board. Each add_node call places a component on the board. add_edge and add_conditional_edges solder the wires between them. compile() runs the quality check and seals it into a finished board. Once compiled, the board is ready to receive power (invoke) and do its job.

Notice the fundamental ReAct loop embedded in the edges above: agent → tools → agent → tools → ... until the agent decides it's done and routes to END. This Reason-Act cycle is the backbone of nearly every LangGraph tool-using agent. Recognize it, and you'll understand 90% of the graphs you'll ever encounter.

## Module 7: Entrypoint & Invocation

<!-- IMAGE 8: source: Medium CDN (miro.medium.com). -->
![Figure 8](https://miro.medium.com/v2/resize:fit:720/format:webp/1*wQ8GQfJ0BU9EWMCN5I0h4g.png)

### The Concept

This is the launch pad. Everything before was definition. This module is execution. Here you write the code that actually runs the graph, feeds it input, and receives output.

There are two modes of invocation you need to know: invoke for a single run, and streaming for progressive output. You also need to understand config — the dictionary that passes runtime parameters, most importantly the thread_id for memory.

### The Keywords You Need to Know

- **`graph.invoke(input, config)`** — runs the graph to completion and returns the final state. This is synchronous — it waits for the entire graph to finish before returning anything.
- **`graph.stream(input, config)`** — runs the graph and yields intermediate state updates as they happen. Use this for user-facing applications where you want to show progress in real time.
- **`config`** — a dictionary you pass to invoke or stream. The most important key is {"configurable": {"thread_id": "some_id"}}. The thread_id is like a session ID — it tells the checkpointer which memory context to load and save. Users with different thread_ids get completely separate memory.
- **`HumanMessage(content=...)`** — how you wrap user input before feeding it to the graph.

### The Standard Template

```python
# ============================================================
# MODULE 7: ENTRYPOINT & INVOCATION
# ============================================================
if __name__ == "__main__":
    
    # ── Config: defines this conversation's memory session ──
    # Change thread_id to start a fresh conversation.
    # Keep the same thread_id to continue an existing one.
    config = {"configurable": {"thread_id": "user-session-001"}}
    
    # ── Single Invocation (synchronous) ─────────────────────
    user_input = "What is the current price of Bitcoin?"
    
    result = graph.invoke(
        input={"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    
    # The result is the final state dictionary.
    # Access the last message to get the agent's final answer.
    final_answer = result["messages"][-1].content
    print(f"Agent: {final_answer}")
    
    # ── Streaming Invocation (for real-time output) ──────────
    for chunk in graph.stream(
        input={"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="values"  # Yields the full state after each node runs
    ):
        # Each chunk is a state snapshot. The last message shows progress.
        latest = chunk["messages"][-1]
        if hasattr(latest, "content") and latest.content:
            print(f"[Streaming] {latest.content}")
    
    # ── Multi-turn Conversation Loop ─────────────────────────
    print("\n--- Starting Interactive Session ---")
    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in ("exit", "quit", "bye"):
            break
        
        response = graph.invoke(
            input={"messages": [HumanMessage(content=user_text)]},
            config=config  # Same config = same memory thread
        )
        
        print(f"Agent: {response['messages'][-1].content}\n")
```

## Full Canonical Template: The Complete File

Here is the complete, clean skeleton you can copy into any new project. This is the one file you should bookmark. Replace the placeholder implementations with your own logic, and you have the foundation of any LangGraph agent.

```python
# ============================================================
# LANGGRAPH CANONICAL AGENT TEMPLATE
# Modules: Imports → State → Tools → Nodes → Edges → Assembly → Entrypoint
# ============================================================
# ── MODULE 1: IMPORTS & CONFIGURATION ───────────────────────
import os
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ── MODULE 2: STATE ─────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # Add your custom fields here

# ── MODULE 3: TOOLS ─────────────────────────────────────────
@tool
def my_tool(input: str) -> str:
    """Describe clearly what this tool does and when the LLM should use it."""
    return f"Result for: {input}"
tools = [my_tool]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

# ── MODULE 4: NODES ─────────────────────────────────────────
def agent_node(state: AgentState) -> dict:
    """The reasoning node. Calls the LLM, optionally triggers tool calls."""
    messages = [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ── MODULE 5: EDGES & ROUTING ───────────────────────────────
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Decide: did the LLM call a tool, or did it give a final answer?"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

# ── MODULE 6: GRAPH ASSEMBLY ────────────────────────────────
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)
graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "__end__": END}
)
graph_builder.add_edge("tools", "agent")
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# ── MODULE 7: ENTRYPOINT ────────────────────────────────────
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "session-001"}}
    
    while True:
        user_text = input("You: ").strip()
        if not user_text or user_text.lower() in ("exit", "quit"):
            break
        response = graph.invoke(
            {"messages": [HumanMessage(content=user_text)]},
            config=config
        )
        print(f"Agent: {response['messages'][-1].content}\n")
```

## Advanced Module: Multi-Agent Systems

Once you've internalized the single-agent canonical template, multi-agent systems become far less intimidating. The insight is this: each agent is just a compiled graph, and that compiled graph can itself be a node in a larger "supervisor" graph.

### The Keywords You Need to Know (Multi-Agent)

- **Supervisor node** — a special agent node whose job is not to answer the user but to decide which specialist agent should handle this task. It routes between sub-agents.
- **Subgraph** — a compiled LangGraph graph that you register as a node in another graph. It receives and returns state just like any regular node function.
- **Command** — a newer LangGraph pattern (available in LangGraph 0.2+) where a node can return both a state update and a routing instruction in a single return value. It replaces the need for separate conditional edges in some multi-agent patterns.

### The Multi-Agent Structural Template

```python
# ── MULTI-AGENT PATTERN ─────────────────────────────────────
# Each specialist is a compiled graph (a subgraph)

# Sub-agent 1: A researcher
researcher_graph = StateGraph(AgentState)
# ... (built with its own nodes, edges, and tools)
researcher = researcher_graph.compile()
# Sub-agent 2: A writer
writer_graph = StateGraph(AgentState)
# ... (built with its own nodes, edges, and tools)
writer = writer_graph.compile()

# ── SUPERVISOR NODE ─────────────────────────────────────────
def supervisor_node(state: AgentState) -> dict:
    """Decides which sub-agent should handle the current task."""
    # The supervisor LLM decides: "researcher" or "writer" or "FINISH"
    response = supervisor_llm.invoke(state["messages"])
    return {"messages": [response], "next_agent": response.content}

def route_to_agent(state: AgentState) -> Literal["researcher", "writer", "__end__"]:
    """Routes to the appropriate sub-agent based on supervisor's decision."""
    return state.get("next_agent", "__end__")

# ── SUPERVISOR GRAPH ────────────────────────────────────────
supervisor_builder = StateGraph(AgentState)
supervisor_builder.add_node("supervisor", supervisor_node)
supervisor_builder.add_node("researcher", researcher)  # Subgraph as a node!
supervisor_builder.add_node("writer", writer)          # Subgraph as a node!
supervisor_builder.set_entry_point("supervisor")
supervisor_builder.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {"researcher": "researcher", "writer": "writer", "__end__": END}
)
supervisor_builder.add_edge("researcher", "supervisor")
supervisor_builder.add_edge("writer", "supervisor")
supervisor_graph = supervisor_builder.compile(checkpointer=MemorySaver())
```

Notice how the multi-agent pattern is identical in structure to the single-agent pattern. The same seven modules apply. The only difference is that some of your "nodes" are themselves entire compiled graphs. The mental model scales cleanly.

## The Keyword Reference Card

Here is a condensed reference you can print or pin. Every important concept from this article in one place.

**State Keywords** — `TypedDict` — defines the shape of state. `Annotated[T, reducer]` — attaches a reducer to a field. `add_messages` — the standard reducer for the messages list (appends instead of replaces). `operator.add` — reducer for accumulating lists or numbers.

**LLM Keywords** — `ChatOpenAI` / `ChatAnthropic` — the LLM class. Always named llm. `bind_tools(tools)` — tells the LLM about available tools. `invoke(messages)` — calls the LLM and returns a response.

**Message Keywords** — `HumanMessage` — user input. `AIMessage` — LLM output. `SystemMessage` — your instructions to the LLM (the system prompt). Always a list when passed to invoke.

**Tool Keywords** — `@tool` — decorator that turns a Python function into an LLM-callable tool. The docstring is the tool's description. `ToolNode(tools)` — pre-built node that executes tool calls automatically. `tools_condition` — pre-built router that checks if the LLM made a tool call.

**Graph Keywords** — `StateGraph(State)` — creates the graph builder. `add_node(name, fn)` — registers a node. `set_entry_point(name)` — declares the first node. `add_edge(A, B)` — unconditional wire from A to B. `add_conditional_edges(source, router, mapping)` — conditional wire based on router's return value. `compile(checkpointer=...)` — seals and finalizes the graph. `END` — the terminal constant.

**Invocation Keywords** — `graph.invoke(input, config)` — run to completion, return final state. `graph.stream(input, config)` — run and yield state updates progressively. `config = {"configurable": {"thread_id": "..."}}` — the memory session identifier. `MemorySaver()` — in-memory checkpointer for persistent conversation memory.

## Conclusion: The Muscle Memory of LangGraph

The goal of this article was never to teach you LangGraph from scratch. It was to give your brain a stable, repeatable scaffold that you can reach for automatically — the way a musician reaches for a chord progression, or a chef reaches for mise en place.

The seven-module structure — Imports → State → Tools → Nodes → Edges → Assembly → Entrypoint — is your chord progression. The keywords in each module are your notes. The canonical template is your sheet music.

Every LangGraph agent you will ever build, from a simple chatbot to a complex multi-agent pipeline with dozens of nodes, fits inside this structure. The complexity grows, but the structure remains the same. That's the point. That's what makes it a standard.

Start simple. Build the minimal ReAct loop: one agent_node, one tool_node, one conditional edge using tools_condition. Get it working. Then add a second node. Then a second agent. The scaffold holds at every level.

The map is now in your hands. The territory, as always, is built one node at a time.

Want to go further? Explore LangGraph's official documentation at [python.langchain.com/docs/langgraph](https://python.langchain.com/docs/langgraph) for persistence backends, human-in-the-loop patterns, and deployment with LangGraph Platform.

---

**Tags:** Langchain · Langgraph · Ai Agnet · Mental Models · Code

*Written by Bessie Delight Kekeli — AI engineer by day, writer by night. Turning cutting-edge tech into articles anyone can understand.*
