# Exercise — Supervisor Agent Pattern in LangGraph

## What you'll build

A **supervisor agent**: a coordinator that repeatedly decides which worker to run
next, regains control after each one, and decides when the task is complete. It's
the **router and loop patterns combined** — it branches to a worker (router-style)
and workers return to it so it can branch again (loop-style).

```
START -> [supervisor] --(FINISH)--> END
            |    ^
            v    | (workers loop back)
      [researcher]  [writer]
```

The supervisor picks `researcher` first, gets facts back, then picks `writer`,
gets a draft back, then decides the task is done and routes to `FINISH`. A
**termination guard** guarantees it can't loop forever.

## Files

- `exercise-supervisor-agent.ipynb` — starter notebook with `TODO` / `____` blanks
- `solution-supervisor-agent.ipynb` — complete answer key, with a streaming cell showing the hand-offs and extension ideas
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

Talks to Ollama via the `ChatOpenAI` + `base_url` bridge — no API key needed.

## Your tasks (in the starter notebook)

1. **Complete the state** — add `draft` and `next` to `SupervisorState`.
2. **Complete the termination guard** — in `supervisor`, once both workers have
   run, set `state["next"] = "FINISH"` and return. This is what stops the loop.
3. **Implement the `writer`** worker, following the given `researcher`.
4. **Write the router function** — return `state["next"]`.
5. **Add the conditional edge** — map `researcher`/`writer` to their nodes and
   `FINISH` to `END`.
6. **Add the loop-back edges** — `researcher → supervisor` and
   `writer → supervisor`. This is the defining feature: workers return to the
   coordinator instead of ending.

## Learning goals

- See how **branching out and looping back combine** into a coordinator that runs
  a variable number of steps.
- Understand why a supervisor **needs a termination guarantee** — the same lesson
  as the loop exercise: something in the state must advance toward an exit (here,
  each worker fills a field, and the guard fires once both are set).
- Recognise that the **worker → supervisor edge** (not worker → END) is what turns
  a one-shot router into a multi-step coordinator.

## How it connects

This is essentially what `create_agent` does internally: a coordinator (the model)
that repeatedly picks a tool, gets the result back, and decides when to finish.
You've now built that machinery by hand.

Progression across the mini-series:

| Pattern | Shape | Edges |
|---------|-------|-------|
| Sequential | fixed line `A → B → C` | fixed |
| Loop | repeat a node | conditional (branch back) |
| Router | one-of-N, once | conditional (branch out) |
| **Supervisor** | coordinate N, repeatedly | conditional out **+** loop back |

## Extension ideas (in the solution notebook)

- Add a 3rd worker (e.g. `reviewer` that critiques the draft).
- Let the supervisor use structured output to choose the next worker.
- Add a bounded `revisions` counter so writer/reviewer can iterate a fixed number
  of times — combining supervisor with an explicit loop guard.
