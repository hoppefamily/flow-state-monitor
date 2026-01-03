# Copilot Implementation Specification – Flow State Monitor

## Goal

Implement a deterministic market signal detector that identifies:
- when market behavior becomes forced (ENTRY)
- when forced behavior exhausts (EXIT)

The system must be rule-based, explainable, and reproducible.
No machine learning.

---

## Inputs

Daily time series:
- `borrow_rate` (percentage)
- `close_price`
- optional: `volatility`

Optional flags already exist in CLI.

---

## Core Concepts

The system exposes two binary states:

### market_state
- OFF = market is elastic, no constraint
- ON  = elasticity broken (structural tension exists)

### flow_state
- OFF = no forced behavior
- ON  = forced buying detected

Conceptual mapping:
- market_state=ON & flow_state=OFF → tension (pre-flow)
- market_state=ON & flow_state=ON  → forced flow

---

## Entry Logic (BUY)

BUY occurs only at the transition.

Conditions:
- market_state flips OFF → ON
- flow_state flips OFF → ON
- both flips occur:
  - same day, or
  - within 1 trading day

Late entries are invalid.
Do not buy if both states have been ON for multiple days.

---

## Borrow Rate Momentum (for EXIT)

Define:
- ΔB(t) = borrow_rate(t) - borrow_rate(t-1)

Compute smoothed momentum:
- Use EMA on ΔB
- Default: `ema_span = 3`
- Allow override to `ema_span = 5`

EMA must be used instead of rolling mean.

---

## Exit Logic (SELL)

Exit is NOT price-based and NOT flow_state-based.

Primary exit signal:
- Borrow rate momentum stops increasing

Define:
- `epsilon = 0.05` (percentage points per day)

SELL when:
- EMA(ΔB) < -epsilon
- condition holds for 1 full trading day

This indicates constraint exhaustion.

Do NOT wait for:
- flow_state = OFF
- price reversal
- volatility collapse

---

## Noise Handling

Borrow rates are noisy and may be estimated.
Exact turning points are not observable.

Therefore:
- smooth derivatives
- use deadband (epsilon)
- use persistence (1 day confirmation)

This is required behavior, not optional.

---

## Output Requirements

For each evaluation, print:
- market_state (ON/OFF)
- flow_state (ON/OFF)
- borrow_rate level
- borrow_rate delta
- smoothed borrow momentum
- explicit reason for BUY / SELL / HOLD

Output must be human-readable.

---

## Non-Goals

Do NOT implement:
- forecasting
- ML models
- price prediction
- optimization

This tool detects **constraint transitions**, nothing else.

---

## Implementation Constraints

- Deterministic logic only
- All thresholds configurable
- Defaults conservative
- Prefer clarity over compactness

End of specification.
