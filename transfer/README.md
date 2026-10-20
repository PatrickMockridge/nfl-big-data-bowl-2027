# Transfer extension — which parts of the allocation-gap argument travel?

**Status:** a GitHub-only extension to the 2027 NFL Big Data Bowl entry. It is
not attached to the competition and is not published on Kaggle. The original
v1 judged artifacts are at `c652424`; the v2 writeup keeps the transfer results
outside it. Date-stamped **2026-10-20**.

The judged entry's tiered argument is: a 10 Hz measurement carries a performance
signal the stopwatch misses; the signal is essentially unpriced by draft; the
depth chart rewards status and prior role rather than the measured performance;
the cap pays performance. This folder asks whether the same three-link pattern
appears, more weakly, in other parts of the Big Data Bowl dataset.

The answer is uneven, and that is the point:

- **The measurement link does not travel.** The task-matched drill signal has a
  positive pressure coefficient for interior and edge defensive linemen, but it
  is Holm-borderline after correction (p=0.054–0.061) and adds no
  out-of-sample R² over the stopwatch (interior −0.027, edge +0.015),
  and it is weak for receivers. Tight ends and offensive linemen fail the
  measurement-reliability gates; defensive backs have no usable performance
  residual. The DL positive control reproduces the entry: `burst_z` → pressure
  is **+0.368** (95% CI 0.149 to 0.587, n=64), against the entry's +0.354
  (0.143 to 0.565), with +0.050 incremental R² against the entry's +0.049.
- **The unpriced-signal link travels.** The position-specific drill signal is
  uncorrelated with draft capital in every position (|ρ| ≤ 0.10), while the
  40-yard dash is priced for receivers (ρ=0.335) and defensive backs (ρ=0.398)
  and partly priced for offensive linemen (ρ=0.266).
- **The allocation link travels.** The performance→role coefficient is null in
  every position already estimated; the per-position gap is positive for late
  picks and negative for early picks in WR, OL, and DL, and weaker in TE. DB is
  unidentifiable.
- **The burst is a pressure signal, not a box-score signal.** Interior
  pressure (+0.698) and hurry (+0.729) clear the gates; every box-score outcome
  fails the reliability gate, so its null estimates are descriptive only.
- **The BDB-native reward proxy is status-legible.** Career start rate rises
  from 0.03 for late/UDFA players to 0.56 for early picks; measured performance
  adds nothing (−0.017, p=0.27) once draft is controlled.

**Tier label:** Tier 1 descriptive only. No dollar model, no two-agent model, no
causal claim. The Tier 2 assumptions are used only as directional predictions.

## Read in this order

1. [`writeups/00_protocol.md`](writeups/00_protocol.md) — the frozen template and
   the disclosed implementation corrections.
2. [`writeups/01_drill_translation.md`](writeups/01_drill_translation.md) — L1,
   the measurement link.
3. [`writeups/02_signal_link.md`](writeups/02_signal_link.md) — L2, the unpriced
   signal.
4. [`writeups/03_allocation_gap.md`](writeups/03_allocation_gap.md) — L3, the
   allocation gap by position.
5. [`writeups/04_breadth_and_career.md`](writeups/04_breadth_and_career.md) —
   outcome breadth and the career reward ladder.
6. [`writeups/05_what_transfers.md`](writeups/05_what_transfers.md) — the
   synthesis: what travels, what does not, and what would change the answer.

## Reproduce

```bash
python scripts/20_transfer_drills.py
python scripts/21_transfer_signals.py
python scripts/22_transfer_breadth.py
python scripts/23_transfer_career.py
python scripts/24_transfer_figures.py
```

Outputs are written to `outputs/transfer/` (gitignored). The protocol is
`docs/TRANSFER_PROTOCOL.md`; the configuration block is the `transfer:` section
of `config.yaml`.

## Data and limits

- Competition data only. No external salary or contract data.
- 510 Combine cohort players, 2023–2025 draft classes; 505 have at least one
  tracked skill drill and enter the signal layer. Five testable position groups:
  DB 118, DL 118, OL 121, TE 42, WR 106. LB (n=3) and OTHER (n=3) are excluded;
  there are no RB or QB rows in the Combine file.
- `game_tracking` covers only the cohort players on each play (mean 1.6, max 6),
  not all 22; relative defender–receiver metrics are out of scope.
- All estimates are observational and descriptive. The role and career outcomes
  are cumulative or mechanical in part; the caveats are stated in each writeup.
- The judged entry and `implications/` are unchanged.
