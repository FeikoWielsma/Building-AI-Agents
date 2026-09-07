# Exercise 1: Exploring Neural Networks with TensorFlow Playground

## Goal

Get an intuitive, hands-on feel for how an artificial neural network learns to
separate patterns in data — **without writing any code**. You build the network
by clicking, press play, and watch it train live. The second half of the
exercise shows why harder patterns need a *bigger* network.

## What is TensorFlow Playground?

[TensorFlow Playground](https://playground.tensorflow.org) is a free, browser-based
simulator of a small feed-forward neural network. Everything runs locally in the
browser — nothing is installed and nothing is sent to a server. You choose a
dataset, decide which input features to feed in, add or remove hidden layers and
neurons, pick an activation function, and press **Play** to train. The output
panel visualises, in real time, how the network is carving up the 2‑D plane to
classify the points.

The colours are the key to reading the screen:

- **Orange vs. blue dots** — the two classes the network must separate.
- **Background shading** — the network's current prediction for every point in
  the plane. As training progresses, the shaded regions should grow to match the
  dot colours.
- **Connection thickness and colour** — the weight of each link between neurons.
  Thicker lines carry more influence.

## A quick tour of the controls

| Control | What it does |
|---|---|
| **Dataset (DATA)** | Choose the pattern to learn: Circle, Exclusive-or, Gaussian, or **Spiral** (hardest). |
| **Ratio / Noise / Batch size** | How much data is training vs. test, how messy it is, and how many samples per training step. |
| **Features (FEATURES)** | Which inputs the network sees: `X₁`, `X₂`, and derived features like `X₁²`, `X₂²`, `X₁X₂`, `sin(X₁)`, `sin(X₂)`. |
| **Hidden layers / neurons** | Use the **+ / –** buttons to add or remove layers, and per-layer buttons to add or remove neurons. This is the network's *capacity*. |
| **Learning rate** | How big a step the network takes each update. Too high overshoots; too low crawls. |
| **Activation** | The non-linearity in each neuron: Tanh, ReLU, Sigmoid, or Linear. |
| **Regularization** | Optional L1/L2 penalty to discourage overly complex solutions. |
| **Problem type** | Classification (separate classes) or Regression (predict a value). |
| **Epoch** | A counter of how many passes over the data have been trained. |
| **Test / Training loss** | Error on unseen vs. seen data — lower is better. Watch these fall as it learns. |

## Part A — Observe how the network learns a simple pattern

1. Open <https://playground.tensorflow.org>.
2. Select the **Circle** dataset (top-left, the default).
3. Leave the default settings: features `X₁` and `X₂`, one or two small hidden
   layers, Tanh activation, learning rate `0.03`.
4. Press **Play** and watch.

**What to notice:**

- The **loss numbers** drop and the **background shading** gradually forms a
  circular boundary that matches the dot pattern.
- Hover over a neuron to see the little region *that individual neuron* has
  learned to respond to. The final output is a weighted **combination** of these
  simpler pieces — this is the core idea of a neural network.

Try the **Exclusive-or** and **Gaussian** datasets too. A small network handles
all three fairly quickly.

## Part B — The Spiral: why harder patterns need a bigger network

Now switch the dataset to **Spiral**. Press Play with the default small network
and watch it struggle — the loss stays high and the background never wraps
cleanly around the intertwined arms.

The spiral is *not linearly separable* and its boundary is highly curved, so the
network needs more **capacity** — more layers and more neurons — to bend the
decision boundary tightly enough.

**Increase the capacity step by step and re-train after each change:**

1. Add a second and third hidden layer (the **+** above the layers).
2. Add neurons to each layer (aim for roughly 6–8 per layer).
3. Try switching the **activation** from Tanh to **ReLU** — it often learns the
   spiral faster and more reliably.
4. Give it time: the spiral can take **hundreds to thousands of epochs**.

**A configuration that reliably learns the spiral** (a good starting point, not
the only answer):

- Dataset: **Spiral**, Noise: `0`
- Features: `X₁`, `X₂` only (so the *network*, not hand-picked features, does the work)
- Hidden layers: **4**, with about **8, 8, 6, 4** neurons
- Activation: **ReLU**
- Learning rate: `0.03`
- Let it run until the test loss drops well below `0.1`

You'll see the shaded background slowly grow two interlocking spiral arms until it
matches the data.

> **Shortcut worth trying afterwards:** go back to a *small* network but switch on
> extra features such as `sin(X₁)` and `sin(X₂)`. The spiral becomes much easier,
> because you've handed the network better-shaped inputs. This illustrates the
> trade-off between **network depth** and **feature engineering** — two different
> ways to give a model the power to solve a hard problem.

## Reflection questions

1. What happens to the training and test loss as you add layers and neurons? Do
   they always improve together?
2. When you add *too many* neurons and turn up the noise, does the boundary start
   fitting the noise instead of the pattern? (This is **overfitting** — the test
   loss stops improving or gets worse while training loss keeps dropping.)
3. How does changing the **learning rate** affect training — try `0.001` and `1`
   and describe the difference.
4. Compare **Tanh** and **ReLU** on the spiral. Which converges faster?

## Key concepts introduced

- **Neuron / hidden layer** — the building blocks; each layer transforms the
  output of the previous one.
- **Feature** — an input the network receives; derived features can make a
  problem easier.
- **Activation function** — the non-linearity that lets the network model curved
  boundaries.
- **Capacity** — more layers and neurons = ability to learn more complex shapes,
  at the risk of overfitting.
- **Loss** — the error the network is trying to minimise.
- **Epoch** — one full pass over the training data.
- **Overfitting** — memorising noise instead of learning the true pattern.

## Reference

TensorFlow Playground: <https://playground.tensorflow.org>
