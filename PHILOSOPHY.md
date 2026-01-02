# Philosophy

## What this tool is about

This project is not about predicting markets.
It is not about finding better entries.
It is not about maximizing returns.

It is about **identifying when non-optional participants are active**.

---

## Core idea

Markets move for different reasons:

1. **Information** - news, fundamentals, sentiment
2. **Optional flows** - discretionary buyers and sellers
3. **Non-optional flows** - forced participants (shorts covering, margin calls, rebalancing)

This tool focuses on detecting **non-optional flows** driven by short covering.

When borrow rates spike, shorts face increasing costs and pressure.
They must cover - buying is not optional for them.
This creates predictable buying pressure independent of fundamentals.

---

## Flow States

The monitor classifies the market into three flow states:

- **ON**
  Forced buying pressure is active.
  High borrow rates, rising momentum, price spikes.
  Non-optional participants are actively buying.

- **WEAKENING**
  Forced buying pressure exists but is diminishing.
  Borrow rates still elevated but declining.
  The forced buying wave is losing strength.

- **OFF**
  No significant forced buying pressure detected.
  Low borrow rates, stable conditions.
  Market flow appears normal and optional.

The state is not a prediction.
It is an **observation of current flow dynamics**.

---

## What the tool deliberately does NOT do

- No predictions about future price direction
- No buy/sell recommendations
- No profit targets or stop losses
- No backtests or performance claims
- No intraday signals
- No optimization or fitting

Adding any of these would change the nature of the project.

---

## Design principles

- Observable metrics over predictive models
- Transparency over complexity
- Daily data over intraday noise
- Deterministic logic over probabilistic inference
- Flow dynamics over fundamental analysis

If two people run the tool on the same data and get different results,
the design is wrong.

---

## How it should be used

This tool is meant to support **disciplined exit decisions**.

- **Flow State = ON**
  → Pressure is active. Riding the wave may be appropriate.

- **Flow State = WEAKENING**
  → Pressure is declining. Consider exit timing.

- **Flow State = OFF**
  → No forced pressure. Flow-based thesis no longer supported.

The tool does not tell you when to enter.
It tells you **when the flow condition that justified entry is changing**.

---

## Key insight

Forced buying pressure is temporary by nature.

Shorts eventually cover or get stopped out.
Borrow rates eventually normalize.
The forced buying wave always ends.

This tool exists to monitor **when that wave is active, weakening, or gone**.

---

## Final note

Flow-based opportunities depend on correctly identifying when non-optional participants are active.

This project exists to automate that identification.
