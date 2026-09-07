# Exercise — Sequential Agent Pattern in LangGraph

## What you'll build

A **sequential agent**: the simplest multi-agent shape in LangGraph. Several
specialised nodes each do one job and run in a **fixed order**, passing a shared
state object down the line. No branching, no loops — just
`START → A → B → C → END`.

The concrete task is a small content pipeline that turns a single topic into a
polished one-sentence summary:

```
topic  ->  [outline]  ->  [draft]  ->  [polish]  ->  final
```

Each stage is an LLM-backed node with its own prompt and role:

| Stage | Node | Reads | Writes | Job |
|-------|------|-------|--------|-----|
| 1 | `make_outline` | `topic` | `outline` | Turn the topic into 3 bullet points |
| 2 | `write_draft` | `outline` | `draft` | Expand the outline into a paragraph |
| 3 | `polish` | `draft` | `final` | Compress the paragraph to one sentence |

## Files

- `exercise-sequential-agent.ipynb` — starter notebook with `TODO` / `____` blanks to fill in
- `solution-sequential-agent.ipynb` — complete answer key with a bonus streaming cell and extension ideas
- `README.md` — this file

## Prerequisites

- **Ollama** running locally with the model pulled:
  ```
  ollama pull qwen3.5:4b
  ```
- Python packages (the notebook installs them in its first cell):
  ```
  pip install langgraph langchain-openai
  ```

The notebook uses the `ChatOpenAI` + `base_url` bridge to talk to Ollama, so no
API key is needed.

## Your tasks (in the starter notebook)

1. **Complete the state** — add the missing `draft` and `final` fields to
   `PipelineState`.
2. **Implement `write_draft`** — follow the given `make_outline` pattern: read
   `state["outline"]`, build a prompt, call the LLM, store the result in
   `state["draft"]`.
3. **Implement `polish`** — read `state["draft"]`, ask the LLM to compress it to
   one sentence, store it in `state["final"]`.
4. **Build the graph** — register the two remaining nodes and wire the sequential
   edges: `START → outline → draft → polish → END`.
5. **Run it** — pick a topic and invoke the graph.

## Learning goals

- See how a **state object flows through a chain of nodes**, each one reading a
  field the previous node produced and writing a new one.
- Understand that a node is just a function `State -> State` — the same shape you
  saw in the earlier graph exercises, now backed by an LLM.
- Recognise the **sequential pattern** as the baseline before conditional edges
  (routers, loops) and other multi-agent patterns (supervisor, swarm) add
  complexity on top.
- Notice that specialisation lives in the **prompt per node**: one model, three
  different jobs, because each node prompts it differently.

## How it connects

This is the LLM-backed version of the plain `START → echo → END` graph you built
earlier. Each `create_agent` you've used is, under the hood, a graph of nodes
passing a `{"messages": [...]}` state around — this exercise is that machinery
with three hand-written nodes so the data flow is fully visible.

## Extension ideas (in the solution notebook)

- Add a 4th stage `translate` that renders `final` into Dutch.
- Give each node a different model to see the sequence mix models per stage.
- Replace the hand-written node functions with `create_agent` agents to build the
  same sequence from full agents.
