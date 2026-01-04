# Money Flow vs. Narrative Flow: Understanding the Boundary

## The Analytical Framework

**flow-state-monitor** operates in the **Money Flow Domain** - it detects price movements driven by mechanical, structural constraints in the market (specifically short covering pressure). However, not all market movements are driven by money flow mechanics.

## The Boundary

```
MONEY FLOW DOMAIN          |  NARRATIVE FLOW DOMAIN
(Mechanical Pressure)      |  (Sentiment & Story)
---------------------------|---------------------------
• Short squeezes           |  • Leadership changes
• Forced covering          |  • Strategic pivots
• Borrow rate spikes       |  • Earnings surprises
• Structural constraints   |  • Market repositioning
• Gamma squeezes           |  • Uncertainty events
                          |  • Sentiment shifts
```

## When flow-state-monitor Works Best

**Money Flow Domain** - Mechanically forced moves:
- High short interest stocks
- Rising borrow rates creating pressure
- Forced buying from shorts covering
- Examples: Heavily shorted stocks, meme stocks during squeezes

## When flow-state-monitor Shows Limitations

**Narrative Flow Domain** - Story-driven moves:
- Major news events
- Leadership transitions
- Strategic announcements
- Fundamental regime changes

### Perfect Example: Berkshire Hathaway (BRK.B)

```bash
$ flow-state-monitor BRK.B

MARKET STATE: OFF
FLOW STATE: OFF
BORROW RATE: 3.10% (LOW)

RELATIVE STRENGTH:
BRK.B: -2.84%
vs SPY: underperforming by -3.38%
vs QQQ: underperforming by -2.64%
```

**Analysis:**
- ✅ **Correctly identifies**: No money flow pressure (low borrow rate, no shorts)
- ✅ **Shows underperformance**: Stock is weak vs. benchmarks
- ⚠️ **Misses the story**: Warren Buffett succession/transition narrative

**Why this happens:**
1. **No one shorts Berkshire** - It's institutional-grade, Buffett's reputation
2. **But massive narrative** - Succession is a fundamental regime change
3. **Volatility without mechanical pressure** - Pure sentiment/positioning
4. **flow-state-monitor correctly says "not my domain"**

**What's actually happening:**
- Market is repricing based on **uncertainty** about post-Buffett era
- Investors repositioning based on **narrative** (leadership transition)
- This is **sentiment-driven**, not **mechanically-forced**

## Using Both Tools Together

For comprehensive market analysis, you need both frameworks:

### flow-state-monitor (Money Flow)
**Use when:**
- Analyzing stocks with significant short interest
- Tracking borrow rate changes
- Identifying forced buying pressure
- Detecting mechanical squeezes

**Signals:**
- Flow ON + Outperforming = Strong squeeze signal
- Flow ON + Underperforming = Weak/questionable signal
- Flow OFF + Any performance = No mechanical pressure

### NarrativeFlow (Narrative Flow)
**Use when:**
- Major news events (earnings, guidance, leadership)
- Strategic announcements (M&A, pivots, restructuring)
- Market sentiment shifts
- Uncertainty events

**Signals:**
- High narrative volatility + Price movement = Story-driven
- Low narrative volatility + Price movement = Check money flow

## Decision Matrix

| Flow State | Performance vs Market | Money Flow Signal | Check Narrative? |
|------------|----------------------|-------------------|------------------|
| ON | Outperforming | ✅ Strong | Optional |
| ON | Underperforming | ⚠️ Weak | ✅ Yes - conflict |
| OFF | Outperforming | 💡 Not flow-driven | ✅ Yes - what's driving? |
| OFF | Underperforming | ✓ Consistent | ✅ Yes if unusual |

## Examples by Domain

### Pure Money Flow (flow-state-monitor excels)
- **GameStop (GME)** during 2021 squeeze
- **AMC** during meme stock rallies
- Any stock with: High SI% + Rising borrow rates + Price surge

### Pure Narrative Flow (NarrativeFlow excels)
- **BRK.B** - Buffett succession
- **AAPL** - New product launches
- **NVDA** - AI narrative shifts
- Any stock with: Major news + Volatility + Low short interest

### Hybrid (Both tools valuable)
- **TSLA** - Often has both short pressure AND narrative events
- **COIN** - Crypto narrative + significant short interest
- Stocks with: News catalysts + High short interest

## Practical Workflow

1. **Run flow-state-monitor first**
   - Check if mechanical pressure exists
   - Look at Flow State + Relative Strength

2. **Interpret the results**
   - Flow ON + Strong performance = Money flow likely driving
   - Flow OFF = Check for narrative drivers

3. **Run NarrativeFlow if needed**
   - Flow OFF but big moves = Narrative-driven
   - Flow ON but weak performance = Narrative conflict?

4. **Synthesize**
   - Best setups: Flow + Narrative aligned
   - Conflicts: One says buy, other says sell = caution
   - Neither: Quiet, no major drivers

## Summary

**flow-state-monitor tells you:** "Is there mechanical pressure forcing buying?"

**NarrativeFlow tells you:** "Is there a story driving sentiment?"

**BRK.B example shows:** Sometimes the answer to the first question is "no" but there's still significant price action - that's when you need the narrative lens.

Use the right tool for the right domain, and use both when you need complete market understanding.
