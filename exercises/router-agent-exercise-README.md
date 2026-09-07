# Exercise — Router Agent Pattern in LangGraph

## What you'll build

A **router agent**: a graph that inspects an incoming request, decides which
specialist should handle it, and dispatches to exactly **one** of several
branches. Unlike the sequential pattern (every node runs, in a fixed order), the
router uses a **conditional edge** to pick a single destination.

```
                          -> [math]      ->
START -> [classify] --->    -> [translate] --> END
                          -> [general]   ->
```

- `classify` is the router's "brain": it reads the question and writes a `route`
  value (`"math"`, `"translate"`, or `"general"`) into the shared state.
- A **conditional edge** runs a `route` function that reads that value and sends
  the state to the matching specialist node.
- Each specialist answers with its own prompt, then the run ends.

## Files

- `exercise-router-agent.ipynb` — starter notebook with `TODO` / `____` blanks
- `solution-router-agent.ipynb` — complete answer key, with a bonus "which branch fired" cell and extension ideas
- `README.md` — this file

## Prerequisites

- **Ollama** running locally with the model pulled:
  ```
  ollama pull qwen3.5:4b
  ```
- Python packages (installed by the notebook's first cell):
  ```
  pip install langgraph langchain-openai
  ```

The notebook talks to Ollama through the `ChatOpenAI` + `base_url` bridge, so no
API key is needed.

## Your tasks (in the starter notebook)

1. **Complete the state** — add `route` and `answer` to `RouterState`.
2. **Implement two specialists** — `translate_specialist` and
   `general_specialist`, following the given `math_specialist`.
3. **Write the router function** — `route(state)` returns the node name stored in
   `state["route"]`.
4. **Add the conditional edge** — map each route value to its specialist node with
   `add_conditional_edges`.
5. **Connect specialists to END** and pick three test questions (one per branch).

## Learning goals

- Understand the **conditional edge** — the mechanism that turns a straight-line
  graph into a branching one. `add_conditional_edges(source, fn, mapping)` runs
  `fn` after `source` and uses its returned string to choose the next node.
- See the **decide-then-dispatch split**: one node (`classify`) writes the
  decision into state; the router function only reads it. Keeping classification
  and dispatch separate makes the graph easy to extend.
- Notice that adding a branch is a **three-line change**: a new node, a new route
  value in the classifier, and a new entry in the conditional-edge mapping.

## How it connects

This is the same conditional-edge machinery you saw in the loop exercise
(`add_conditional_edges`), but pointed *outward* to different specialists instead
of *backward* to repeat a node. It's also exactly how `create_agent` decides
"call a tool" vs "finish" under the hood — a router choosing the next node based
on state.

Progression across the mini-series:

| Pattern | Shape | Edge type |
|---------|-------|-----------|
| Sequential | `A -> B -> C` | fixed edges |
| Loop | `A -> B -> (back to A?)` | conditional (branch back) |
| **Router** | `classify -> one of N` | conditional (branch out) |

## Extension ideas (in the solution notebook)

- Add a 4th specialist (e.g. `code`) — three small edits.
- Swap the string-parsing classifier for structured output (a Pydantic label) for
  a more robust route.
- Chain the router *into* a sequential pipeline: route first, then run the chosen
  specialist through a multi-stage sequence.
