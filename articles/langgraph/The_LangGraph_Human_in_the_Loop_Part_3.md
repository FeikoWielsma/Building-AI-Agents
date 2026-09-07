# LangGraph Human-in-the-Loop: Pausing, Reviewing, and Rewinding Your Agent

*Part 3 of the LangGraph Mental Model series — building on the canonical structure and memory patterns from Part 2.*

**Bessie Delight Kekeli** · 13 min read · 5 days ago

*For other parts of the series:* [Part 0](https://medium.com/@bessiedelight/the-building-blocks-of-langgraph-1975904edac8) , [Part 1](https://medium.com/towards-artificial-intelligence/the-langgraph-mental-model-a-standardized-architecture-guide-for-every-agent-youll-ever-build-d02265f3bebf) , [Part 2](https://medium.com/@bessiedelight/langgraph-memory-the-complete-practical-guide-to-managing-what-your-agent-remembers-d865d505a59e) , [Part 3](https://medium.com/@bessiedelight/langgraph-human-in-the-loop-pausing-reviewing-and-rewinding-your-agent-4028bd05b049)

<!-- IMAGE 1 (lead image): source Medium CDN (miro.medium.com). -->
![Figure 1](https://miro.medium.com/v2/resize:fit:720/format:webp/1*h5aKS5Pgk7cMD-t_2VQVRQ.png)

> **What this article assumes:** You're comfortable with the seven-module structure (Imports → State → Tools → Nodes → Edges → Assembly → Entrypoint) and the memory patterns from Part 2 (summarization, checkpointers, thread_id). Every pattern here is built on top of a checkpointer — without one, none of this works.

## Why Human-in-the-Loop Matters More Than Almost Anything Else

Here's the uncomfortable truth about autonomous agents: the moment you give an LLM the ability to act — send an email, delete a file, charge a credit card, push code — you've created something that can make an expensive mistake at machine speed, with no one watching.

Human-in-the-loop (HITL) is not a "nice to have" feature bolted onto an agent. It is the architecture pattern that makes agents with real-world tools safe to deploy. And the good news is that LangGraph was built around exactly this problem from day one — its entire checkpointing system (which you learned in Part 2) exists largely to make HITL possible.

This article covers the patterns that show up in real production systems, in order of how often you'll actually use them:

- Pausing before risky actions (the interrupt() pattern — the modern standard)
- Editing state during a pause (correcting the agent before it continues)
- Time travel (replaying and branching from any past point in a conversation)

We're deliberately leaving out things that sound impressive in tutorials but rarely show up in real codebases — token-by-token streaming internals, the full LangGraph Studio SDK, and the older NodeInterrupt exception class (superseded by interrupt()). If you need those later, they're easy to pick up once you have this foundation. What you need for 95% of real HITL agents is in this article.

## The Core Concept: Interrupt and Resume

Every HITL pattern in LangGraph reduces to the same two-step dance:

```
1. interrupt()  →  Graph pauses. State is saved. Control returns to your code.
2. Command(resume=...)  →  Graph picks up exactly where it paused, with your input.
```

That's it. Everything else in this article is variations on this theme — where you call interrupt(), what data you pass into it, and what you do with the response.

### The Keywords You Need to Know

- **`interrupt(value)`** — a function (from langgraph.types) you call inside a node. It pauses graph execution at that exact point, saves the full state to the checkpointer, and surfaces value to whoever is running the graph. Execution genuinely stops — no background thread is spinning, no resources are consumed. The thread can sit paused for months.
- **`Command(resume=value)`** — what you pass to graph.invoke() or graph.stream() to unpause a graph. The value you provide becomes the return value of the interrupt() call that paused it — exactly as if interrupt() were a synchronous input() call that just received an answer.
- **`__interrupt__`** — the special key that appears in the graph's output when execution pauses. Check for this key to know "did my agent just stop and ask for input?"
- **`checkpointer`** — mandatory for any of this. Without a checkpointer (MemorySaver, SqliteSaver, PostgresSaver — from Part 2), there is no state to pause and resume. This is the single most common reason HITL code fails for beginners: they forget to compile with a checkpointer.

## Pattern 1: Tool Call Approval (The #1 Real-World Use Case)

This is, by a wide margin, the most common HITL pattern in production. The shape is always the same: your agent decides to call a tool that does something real — send an email, run a database query, place an order — and a human needs to approve it first.

### The Mental Model

Think of this like a manager co-signing a check. The employee (the LLM) fills out the check and hands it over. Nothing happens until the manager (the human) signs it. If the manager says no, the check is voided — no money moves.

### Module 4: The Review Node

```python
# ── IMPORTS needed ───────────────────────────────────────────
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
# ── MODULE 4: NODES ───────────────────────────────────────────
def review_tool_call(state: AgentState) -> dict:
    """Pauses execution to let a human approve, edit, or reject a tool call
    before it actually runs."""
    
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]  # Assume one tool call for simplicity
    
    # interrupt() pauses HERE. The dict below is shown to whoever resumes the graph.
    human_response = interrupt({
        "question": "Approve this action?",
        "tool_name": tool_call["name"],
        "tool_args": tool_call["args"],
    })
    
    # Execution resumes here, with human_response being whatever
    # was passed to Command(resume=...)
    
    if human_response["type"] == "approve":
        # Do nothing - let the tool call proceed as-is
        return {}
    
    elif human_response["type"] == "edit":
        # Replace the tool call's arguments with the human's edits
        last_message.tool_calls[0]["args"] = human_response["edited_args"]
        return {"messages": [last_message]}
    
    elif human_response["type"] == "reject":
        # Short-circuit: skip the tool entirely, tell the LLM why
        return {
            "messages": [
                ToolMessage(
                    content="User rejected this action.",
                    tool_call_id=tool_call["id"]
                )
            ]
        }
```

### Module 6: Wiring It In

```python
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("review_tool_call", review_tool_call)
graph_builder.add_node("tools", tool_node)
graph_builder.set_entry_point("agent")
# Agent decides: call a tool (go through review) or finish
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "review_tool_call", "__end__": END}
)
graph_builder.add_edge("review_tool_call", "tools")
graph_builder.add_edge("tools", "agent")
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

Notice the routing change from Part 1: instead of "tools": "tools", we route to "review_tool_call" first. The review node sits between the agent's decision and the tool's execution — exactly like the manager co-signing the check before it's cashed.

### Module 7: Running and Resuming

```python
config = {"configurable": {"thread_id": "session-001"}}
# ── First call: runs until interrupt() pauses it ─────────────
result = graph.invoke(
    {"messages": [HumanMessage(content="Send an email to the team about the delay")]},
    config=config
)
# Check if the graph paused
if "__interrupt__" in result:
    interrupt_data = result["__interrupt__"][0].value
    print(f"Agent wants to: {interrupt_data['tool_name']}")
    print(f"With arguments: {interrupt_data['tool_args']}")
    
    # Show this to a human (in a real app: render a UI button, Slack message, etc.)
    user_decision = input("Approve? (yes/no): ")
    
    # ── Resume with the human's decision ──────────────────────
    if user_decision.lower() == "yes":
        final_result = graph.invoke(
            Command(resume={"type": "approve"}),
            config=config
        )
    else:
        final_result = graph.invoke(
            Command(resume={"type": "reject"}),
            config=config
        )
    
    print(final_result["messages"][-1].content)
```

This is the complete pattern. Everything else in HITL is a variation: what data you put in interrupt(), and what you do with the resumed value.

## Pattern 2: A Dedicated "Human Feedback" Checkpoint

Sometimes you don't want to interrupt conditionally based on what the LLM decided — you want a guaranteed pause point at a specific stage of your workflow, every single time. Common example: a content-generation agent that always pauses for human review before publishing, regardless of what it generated.

### The Mental Model

This is like a mandatory quality-control gate on an assembly line. Every item passes through this station, every time, no exceptions. The worker at the station can let it through unchanged, send it back for rework, or tweak it themselves.

### Module 4: The Feedback Node

```python
def human_feedback(state: AgentState) -> dict:
    """A guaranteed pause point. Shows the human the latest draft
    and lets them approve, request changes, or edit directly."""
    
    draft = state["messages"][-1].content
    
    feedback = interrupt({
        "question": "Review this draft. Approve, or provide edit instructions.",
        "draft": draft,
    })
    
    if feedback.get("approved"):
        return {}  # Pass through unchanged
    
    # Feedback contains revision instructions — feed back to the agent
    return {
        "messages": [
            HumanMessage(content=f"Please revise based on this feedback: {feedback['notes']}")
        ]
    }
```

### Module 6: Wiring — The Feedback Loop

```python
graph_builder = StateGraph(AgentState)
graph_builder.add_node("writer", writer_node)
graph_builder.add_node("human_feedback", human_feedback)
graph_builder.set_entry_point("writer")
graph_builder.add_edge("writer", "human_feedback")
# After feedback, loop back to writer for revisions, OR end if approved
graph_builder.add_conditional_edges(
    "human_feedback",
    lambda state: "writer" if state["messages"][-1].content.startswith("Please revise") else "__end__",
    {"writer": "writer", "__end__": END}
)
graph = graph_builder.compile(checkpointer=MemorySaver())
```

This is the "review and revise" loop you see in nearly every content-generation, code-review, or research-assistant agent: generate → pause for human → revise if needed → pause again → repeat until approved.

## Pattern 3: Editing State Directly (Manual Correction)

Sometimes a human doesn't just want to approve/reject — they want to directly fix something in the agent's state before it continues. This is the pattern for "the agent got something slightly wrong, let me just correct it myself rather than asking it to retry."

### The Keywords You Need to Know

- **`graph.get_state(config)`** — (from Part 2) returns the current StateSnapshot, including .values (the actual state dict) and .next (which node would run if resumed).
- **`graph.update_state(config, values)`** — directly writes new values into the state at the current checkpoint. This creates a new checkpoint — it doesn't overwrite history, it adds to it. This is important for the time-travel pattern later.
- **`as_node="node_name"`** — an optional argument to update_state. It tells LangGraph "pretend this update was written by node_name." This matters because LangGraph uses the source node of the last update to determine which edges to follow next. Without specifying this correctly, the graph might not resume where you expect.

### The Pattern in Practice

```python
# ── Pause first (using interrupt_before at compile time) ────
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["agent"]  # Always pause before the agent node runs
)
config = {"configurable": {"thread_id": "session-002"}}
# Run until the breakpoint
result = graph.invoke({"messages": [HumanMessage(content="What's 5 + 5?")]}, config)
# ── Inspect what's about to happen ───────────────────────────
snapshot = graph.get_state(config)
print(f"About to run: {snapshot.next}")  # e.g. ('agent',)
print(f"Current messages: {snapshot.values['messages']}")
# ── Directly correct the state ───────────────────────────────
# Suppose the human wants to inject a clarification before the agent responds
graph.update_state(
    config,
    {"messages": [HumanMessage(content="Actually, I meant 5 * 5, not 5 + 5")]},
)
# ── Resume - agent now sees the corrected message ────────────
final = graph.invoke(None, config)  # None = "just resume, no new input"
print(final["messages"][-1].content)
```

### Two Critical Things to Remember

**interrupt_before vs. interrupt():** `interrupt_before=["node_name"]` is set at compile time and always pauses before that node, every single run. `interrupt()` is called inside a node and pauses conditionally, based on logic you write. Use interrupt_before for simple, always-pause debugging or guaranteed checkpoints. Use interrupt() for anything where the pause depends on runtime conditions (which is most real applications).

**Passing None to resume:** when you call `graph.invoke(None, config)`, you're telling LangGraph "don't add new input — just continue from the last checkpoint." This is different from Command(resume=...), which specifically answers a pending interrupt() call. If you used interrupt_before and update_state (not interrupt()), resume with None. If you used interrupt(), resume with Command(resume=...).

## Pattern 4: Time Travel (Replay and Branch)

Time travel is the pattern that turns your checkpoint history into something you can navigate — like commits in a Git history. You can look at any past state, and you can branch from it, creating an alternate timeline without affecting the original.

### The Mental Model

Think of your conversation as a series of save points in a video game. get_state_history shows you every save point. You can load any of them — not just the most recent — and continue playing from there. The original timeline still exists; you've just started a new branch.

### The Keywords You Need to Know

- **`graph.get_state_history(config)`** — (introduced in Part 2) a generator yielding every StateSnapshot ever saved for this thread, newest first. Each snapshot has its own config containing a unique checkpoint_id.
- **`checkpoint_id`** — found inside snapshot.config["configurable"]["checkpoint_id"]. This is the "save point ID." Pass a config containing a specific checkpoint_id to invoke or update_state to operate on that point in history, not the latest one.
- **Replay** — re-running graph.invoke(None, config_with_old_checkpoint_id) re-executes the graph from that old point forward. Since the original checkpoints for that branch already exist, LangGraph is smart about not re-doing work that's already cached — but any node logic from that point forward will run again.
- **Branch** — calling update_state on an old checkpoint creates a new checkpoint that forks off from that point — a new timeline that coexists with the original.

### The Pattern in Practice

```python
config = {"configurable": {"thread_id": "session-003"}}
# Run a few turns normally...
graph.invoke({"messages": [HumanMessage(content="My name is Sam")]}, config)
graph.invoke({"messages": [HumanMessage(content="What's my name?")]}, config)
# ── Find a past checkpoint ────────────────────────────────────
history = list(graph.get_state_history(config))
for snapshot in history:
    print(f"Step {snapshot.metadata['step']}: {len(snapshot.values['messages'])} messages")
# Pick an earlier checkpoint - say, right after "My name is Sam"
target_checkpoint = history[-2]  # Adjust index based on what you printed above
target_config = target_checkpoint.config
# ── Branch: update state AT that old checkpoint ──────────────
# This creates a NEW checkpoint that forks from the old one.
# The original conversation history is untouched.
branch_config = graph.update_state(
    target_config,
    {"messages": [HumanMessage(content="Actually, my name is Alex")]},
)
# ── Continue from the new branch ──────────────────────────────
result = graph.invoke(None, branch_config)
print(result["messages"][-1].content)
# Agent now responds based on the BRANCHED history (name = Alex),
# while the original thread (name = Sam) still exists if you go back to it.
```

### When Time Travel Actually Matters in Production

Time travel isn't something most chatbots need at runtime. Its real value is in three places: debugging (replaying exactly what happened in a failed run to find where it went wrong), evaluation (re-running the same conversation with a different prompt or model to compare outputs — A/B testing without re-doing the whole conversation), and error recovery (a node failed halfway through; rewind to just before it, fix the underlying issue, and resume instead of starting the entire conversation over).

## Bringing It Together: The HITL-Enabled Agent

Here's the canonical template, extending Part 1 and Part 2, with tool-call approval built in. This is the realistic shape of a production agent with a human safety net.

```python
# ============================================================
# LANGGRAPH AGENT WITH HUMAN-IN-THE-LOOP TOOL APPROVAL
# Extends: Part 1 (core structure) + Part 2 (memory)
# ============================================================
# ── MODULE 1: IMPORTS & CONFIGURATION ───────────────────────
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ── MODULE 2: STATE ──────────────────────────────────────────
class State(MessagesState):
    pass  # messages field is inherited; add custom fields if needed
# ── MODULE 3: TOOLS ──────────────────────────────────────────
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email. This is a SENSITIVE action requiring human approval."""
    return f"Email sent to {to} with subject '{subject}'"
tools = [send_email]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)
# ── MODULE 4: NODES ──────────────────────────────────────────
def agent_node(state: State) -> dict:
    messages = [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
def review_tool_call(state: State) -> dict:
    """Pauses for human approval before any tool executes."""
    
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    
    decision = interrupt({
        "tool_name": tool_call["name"],
        "tool_args": tool_call["args"],
    })
    
    if decision["type"] == "reject":
        return {
            "messages": [
                ToolMessage(
                    content="Action rejected by user.",
                    tool_call_id=tool_call["id"]
                )
            ]
        }
    
    if decision["type"] == "edit":
        last_message.tool_calls[0]["args"] = decision["edited_args"]
        return {"messages": [last_message]}
    
    return {}  # approved - pass through unchanged
# ── MODULE 5: ROUTING ─────────────────────────────────────────
def should_continue(state: State) -> Literal["review_tool_call", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "review_tool_call"
    return "__end__"
def after_review(state: State) -> Literal["tools", "agent"]:
    """If the tool call was rejected, the last message is a ToolMessage -
    skip the tools node and go straight back to the agent."""
    last_message = state["messages"][-1]
    if isinstance(last_message, ToolMessage):
        return "agent"
    return "tools"
# ── MODULE 6: GRAPH ASSEMBLY ──────────────────────────────────
graph_builder = StateGraph(State)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("review_tool_call", review_tool_call)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent", should_continue,
    {"review_tool_call": "review_tool_call", "__end__": END}
)
graph_builder.add_conditional_edges(
    "review_tool_call", after_review,
    {"tools": "tools", "agent": "agent"}
)
graph_builder.add_edge("tools", "agent")
graph = graph_builder.compile(checkpointer=MemorySaver())
# ── MODULE 7: ENTRYPOINT ──────────────────────────────────────
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "session-001"}}
    
    result = graph.invoke(
        {"messages": [HumanMessage(content="Email bob@example.com that the meeting moved to 3pm")]},
        config
    )
    
    while "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        print(f"\n Approval needed:")
        print(f"  Tool: {interrupt_info['tool_name']}")
        print(f"  Args: {interrupt_info['tool_args']}")
        
        choice = input("Approve (a) / Edit (e) / Reject (r)? ").strip().lower()
        
        if choice == "a":
            result = graph.invoke(Command(resume={"type": "approve"}), config)
        elif choice == "e":
            new_to = input("New 'to' address: ")
            result = graph.invoke(
                Command(resume={
                    "type": "edit",
                    "edited_args": {**interrupt_info["tool_args"], "to": new_to}
                }),
                config
            )
        else:
            result = graph.invoke(Command(resume={"type": "reject"}), config)
    
    print(f"\nAgent: {result['messages'][-1].content}")
```

## The Updated Keyword Reference Card

This extends the keyword cards from Parts 1 and 2.

**Pausing & Resuming** — `interrupt(value)` — pauses execution inside a node, saves state, surfaces value to the caller. The function call itself "returns" the resume value once the graph is resumed — conceptually like a synchronous input(). `Command(resume=value)` — passed to invoke/stream to answer a pending interrupt(). value becomes the return value of that interrupt() call. `"__interrupt__"` — the key in the graph's output dict indicating execution paused. Check result["__interrupt__"][0].value to see what was surfaced. `interrupt_before=["node_name"]` — compile-time argument that always pauses before the named node. Use for guaranteed, unconditional pause points (debugging, mandatory review gates).

**State Editing** — `graph.get_state(config)` — returns the current StateSnapshot (.values, .next, .config). `graph.update_state(config, values)` — writes new values into state, creating a new checkpoint. Does not erase history. `as_node="node_name"` — tells LangGraph to treat the update as if it came from node_name, affecting which edges are followed on resume. `graph.invoke(None, config)` — resumes from the last checkpoint with no new input (used after interrupt_before + update_state, not for answering interrupt()).

**Time Travel** — `graph.get_state_history(config)` — generator of every StateSnapshot ever saved for a thread, newest first. `checkpoint_id` — unique identifier for a specific save point, found in snapshot.config["configurable"]["checkpoint_id"]. `Replay` — re-invoking from an old checkpoint's config, continuing that exact timeline forward. `Branch` — calling update_state on an old checkpoint's config, forking a new timeline that coexists with the original.

## Decision Guide: Which HITL Pattern Do You Need?

**Your agent calls tools that cost money, send communications, or modify external systems** → Pattern 1 (tool call approval with interrupt()). This is non-negotiable for production agents with real-world side effects.

**Your workflow has a content-generation step that should always be reviewed before moving forward** → Pattern 2 (dedicated human feedback node with a revise loop).

**A human needs to correct or inject information mid-conversation without going through a formal approval flow** → Pattern 3 (interrupt_before + update_state).

**You're debugging a failed run, evaluating prompt changes, or need to recover from an error without restarting** → Pattern 4 (time travel via get_state_history).

## Conclusion: Safety Is a Graph Shape, Not an Afterthought

By now, a pattern across all three parts of this series should be clear: every capability — memory, summarization, persistence, human oversight — is expressed as structure. A node here, an edge there, a field in state. LangGraph doesn't have a special "safety mode" you toggle on. Safety is just another shape your graph can take.

The agents that fail in production aren't the ones whose LLM made a bad call — that's expected and recoverable. The ones that fail are the ones where a bad call had no checkpoint between the decision and the consequence. interrupt() is that checkpoint. It costs you one extra node and one extra edge. It might be the most important node in your entire graph.

With Parts 1 through 3, you now have the complete production scaffold: a standardized structure (Part 1), a strategy for keeping conversations affordable and persistent (Part 2), and a safety net for anything your agent does that actually matters (Part 3). That's the foundation underneath nearly every serious LangGraph application you'll encounter.

This concludes the foundational series. From here, the natural next steps are multi-agent orchestration (supervisor patterns, subgraphs) and long-term memory (cross-session user profiles) — both of which build directly on the State, Node, and Checkpointer concepts established across these three articles.

---

**Tags:** AI · AI Agent · Langchain · Python · Langgraph

*Written by Bessie Delight Kekeli — AI engineer by day, writer by night. Turning cutting-edge tech into articles anyone can understand.*
