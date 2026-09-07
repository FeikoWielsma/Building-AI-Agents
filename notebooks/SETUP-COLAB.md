# Setup : Google Colab (nothing to install)

For everyone joining online, and for anyone whose laptop will not let them
install software. You need a browser and a Google account. Nothing is
installed on your machine, and nothing is downloaded.

The same notebooks still run locally against Ollama ; see `SETUP-LOCAL.md`.
One set of notebooks serves both, so you are not on a cut-down version.

## The course key

Every notebook talks to a shared course model. The key is handed out on the
morning ; it is not in the notebooks and not on this page.

Add it once, and every notebook picks it up :

1. Open any course notebook in Colab.
2. Click the **key icon** (🔑) in the left sidebar.
3. **Add new secret**.
4. Name : `COURSE_API_KEY` — spelled exactly like that.
5. Value : the key from the trainer.
6. Turn **Notebook access** on.

The secret is stored against your Google account, not in the notebook, so it
survives between notebooks and is never shared when a notebook is.

The key is capped and is switched off after the course. Do not commit it
anywhere or paste it into a cell.

## Opening the notebooks

`README.md` at the top of the course repository lists every notebook with an
**Open in Colab** button. Clicking one opens a read-only copy. The first time
you change anything Colab offers to **Save a copy in Drive** ; accept, and that
copy is yours to keep.

## What to expect

- The **first cell of each notebook** installs what it needs. It takes about a
  minute the first time in a session and is instant afterwards.
- A notebook that has sat idle for a while is disconnected. Press
  **Connect**, then **Runtime ▸ Run all** ; nothing is lost.
- No GPU is needed. If Colab offers one, you do not need to accept.

## Working together

Colab notebooks share like any Google document. **Share** in the top right,
then anyone with the link can watch you type, and comment. Useful when you get
stuck : paste the link in the chat and the trainer can look at your actual
notebook rather than guess from a screenshot.

## If something fails

| symptom | what to do |
| --- | --- |
| `COURSE_API_KEY` not found | the secret is misspelled, or *Notebook access* is off |
| A cell asks you to type a key | same thing ; the secret was not picked up |
| `NameError: make_llm` | the first cell was not run ; **Runtime ▸ Run all** |
| Everything is suddenly slow | you were disconnected ; press **Connect** |
| `ModuleNotFoundError` | run the notebook's own `pip install` cell above it |

## A note on privacy

What you type into these notebooks goes to a hosted model in order to be
answered. Treat it like any external service : **do not paste anything
confidential, personal or customer-related from your employer.** The exercises
never need real data, and made-up examples work just as well.
