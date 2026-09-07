# Local setup (Ollama, no cloud)

The whole course runs against a local model. No API key, no network after setup.

Every notebook opens with the same setup cell. It checks whether it is running
in Google Colab and picks accordingly : the hosted course model there, a local
model through Ollama here. There is no variable to set ; nothing below that
cell is provider-specific.

Embeddings always run inside the notebook on a small local model, on both
paths, because the hosted endpoint serves none.

## Once per machine

Install Ollama, then pull the models. Do this **before** the course ; a room
full of laptops pulling several gigabytes at once will not go well.

```powershell
winget install --id Ollama.Ollama
ollama pull qwen3.5:2b          # 2.7 GB, the classroom default
ollama pull nomic-embed-text    # 274 MB, needed from the RAG module on
ollama pull qwen3.5:4b          # 3.4 GB, optional, see below
```

Python dependencies:

```powershell
cd C:\Git\courseWare\courseBuildingAIAgents
uv venv --python 3.12
uv pip install -r notebooks/requirements.txt
```

## Which model

`qwen3.5:2b` is the default because it is fast enough to hold a room's
attention. A two-tool agent exchange lands around 5 seconds and stays there.

`qwen3.5:4b` answers slightly better but is much slower and, more importantly,
much less predictable ; measured runs of the same two-tool exchange on the same
machine ranged from under 4 seconds to over 70. On a laptop without a GPU
assume it is worse. Switch to it only if a machine turns out to be fast.

Change the model in the provider switch cell, or set `COURSE_MODEL` in `.env`
if the notebook you are in reads it.

Two things worth knowing before you stand in front of anyone :

- **The first call after Ollama loads a model is far slower than the rest.**
  Run one cell to warm it up before you start talking.
- **Thinking is disabled on purpose.** The switch cell sends
  `extra_body={"reasoning_effort": "none"}`. Qwen3.5 otherwise reasons before
  every answer, which costs time and buys nothing for these exercises.

  It used to send `{"think": False}`, which is the field the **native** Ollama
  API takes. The OpenAI-compatible `/v1` endpoint the switch cell talks to
  ignores it silently, so thinking was on for the whole course. Measured on
  `qwen3.5:2b`, one short answer costs 117 output tokens with reasoning on and
  3 with it off. Some prompts are worse than slow : the trajectory evaluator in
  `exercise24` filled its whole 4096-token context with reasoning, returned an
  empty string, and raised `OutputParserException`. It works with
  `reasoning_effort`.

## Every session

```powershell
cd C:\Git\courseWare\courseBuildingAIAgents
.venv\Scripts\activate
jupyter lab
```

Ollama runs as a background service on `http://localhost:11434` and needs no
starting. Check it with `ollama list`.

## What still needs the internet

Most of the course does not, but these do :

- The Tavily search and YouTube search demos in module 05 need their own API
  keys and cannot run offline.
- `exercise01` uses the TensorFlow Playground website.
- The first `!pip install` cell in each notebook, unless the environment was
  prepared in advance.

## If something fails

| symptom | cause |
| --- | --- |
| `Connection refused` on `:11434` | Ollama service is not running |
| `model ... not found` | that model was never pulled ; check `ollama list` |
| First cell takes minutes | model loading, this is normal once per model |
| Embedding errors about token length | you are not using `make_embeddings()` from the switch cell |
