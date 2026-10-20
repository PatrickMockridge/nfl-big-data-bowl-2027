# The allocation pattern travels; the measurement does not

**Status:** GitHub-only extension of `implications/`, not part of the judged
entry. Date-stamped 2026-10-20.

## The claim

The entry's measured result is a position-specific pressure signal. Its
structural reading is that three pricing mechanisms see different things: the
stopwatch prices sacks, not pressure; the depth chart prices status and prior
role; the cap prices performance, partly through role. The `transfer/`
extension tested whether that reading travels. The answer is uneven:

- **Measurement does not travel.** DL interior and edge pass-rush drills carry
  a pressure signal; WR is weak; TE, OL, and DB fail reliability or variance
  gates.
- **The unpriced-signal link travels.** The task-matched drill signal is
  uncorrelated with draft capital in every position (|ρ| ≤ 0.10), while the
  40-yard dash is priced for WR (0.335) and DB (0.398), and partly for OL
  (0.266).
- **The allocation link travels.** Performance→role is null in DL, WR, OL, and
  TE; role and draft are positive. The gap runs from positive for late picks to
  negative for early picks in WR, OL, and DL.
- **The cap/pricing link is the portable dollar lever.** It is estimable for
  nine cap-covered position groups; OL and special teams have no individual
  performance in the cap ledger.

The market portfolio follows directly: **price the role, not the stopwatch.**
Position markets carry selection only where a signal is supported, and role
where the allocation pattern is measured. The contract market carries the
pricing correction across positions. Coaching and special teams are descriptive.

## Evidence tiers

| Claim | Tier | Source |
|---|---|---|
| DL burst → pressure reproduces the entry | measured association | `outputs/transfer/drill_translation.csv` |
| EDGE pass-rush signal is borderline | measured association | `outputs/transfer/drill_translation.csv` |
| WR route signal is weak | measured association | `outputs/transfer/drill_translation.csv` |
| TE/OL/DB fail reliability or variance gates | measured gate failure | `outputs/transfer/signal_reliability.csv`, `drill_translation.csv` |
| Drill signals are unpriced by draft | descriptive | `outputs/transfer/signal_pricing.csv` |
| Performance→role is null; gap by draft | descriptive | `outputs/discovery/role_allocation_positions.csv`, `outputs/transfer/gap_by_position.csv` |
| Cap pays performance; role-controlled gap | measured association | `outputs/salary/rent_players.csv`, `outputs/markets/position_pricing.csv` |
| Market and portfolio dollars | inference | `implications/markets/code/market_model.py` |
| Team fits, market readings | reading, date-stamped | `02_adoption.md` in this folder |

## The route-gated rule

Only model a route when the evidence supports it:

- **Selection:** DL interior and EDGE; WR high case only.
- **Role:** DL, WR, OL; TE high case only.
- **Contract:** nine cap-covered position groups; not OL, not special teams.
- **Descriptive:** DB, TE, coaching, special teams.

Unsupported routes are set to zero in the model and labeled `not_modeled` or
`unidentifiable`. They are not silently assumed. This is why most position
markets are small: the measurement does not support a larger claim.

## What the dollars mean

Every dollar figure is an **inference**. The model takes measured or descriptive
anchors — the market value quantiles, the per-position pricing gap, the role
saving — and applies explicit low/base/high assumptions. It does not estimate a
causal effect of adopting the analysis.

The portfolio is deliberately not a sum of every route: position markets count
selection + role, while the free-agency market counts contract pricing. The DL
anchor is shown separately for reconciliation. The low-case sum is the
conservative guide when role and contract decisions share an organizational
driver.
