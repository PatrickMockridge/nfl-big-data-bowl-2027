#!/usr/bin/env python3
"""Build the standalone implications notebook.

The notebook embeds the value-model tables as compressed base64 CSVs, so it
runs without the gitignored `implications/outputs/` directory. It does not
import `value_model` at runtime.
"""

from __future__ import annotations

import base64
import io
import sys
import zlib
from pathlib import Path

import nbformat as nbf
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import value_model as vm  # noqa: E402

OUT = HERE / "implications.ipynb"


def _csv_b64(df: pd.DataFrame) -> str:
    raw = df.to_csv(index=False).encode()
    return base64.b64encode(zlib.compress(raw)).decode()


def _assumptions_frame() -> pd.DataFrame:
    rows = [
        ("Team cap (context)", "cap", "$M"),
        ("Interior DL market value", "market", "$M/yr"),
        ("Rookie cost", "rookie", "$M/yr"),
        ("Hit-rate lift from the signal", "hit_lift", "probability"),
        ("Control window", "years", "years"),
        ("Such picks per year", "picks_per_year", "picks/yr"),
        ("Role-reallocation saving per decision", "role_saving", "$M/yr"),
        ("Role decisions per cycle", "role_decisions", "decisions"),
        ("Reallocation efficiency", "reallocation_eff", "share"),
        ("Contract portfolio", "contract_portfolio", "$M/yr"),
        ("Pricing correction", "pricing_correction", "share"),
        ("Implementation cost", "implementation_cost", "$M/yr"),
        ("Adoption probability", "adoption_prob", "probability"),
    ]
    data = []
    for label, field, units in rows:
        low = getattr(vm.LOW, field)
        base = getattr(vm.BASE, field)
        high = getattr(vm.HIGH, field)
        if units == "probability":
            data.append((label, f"{low:.0%}", f"{base:.0%}", f"{high:.0%}", units))
        elif units == "share":
            data.append((label, f"{low:.1%}", f"{base:.1%}", f"{high:.1%}", units))
        else:
            data.append((label, f"{low:g}", f"{base:g}", f"{high:g}", units))
    return pd.DataFrame(data, columns=["Parameter", "Low", "Base", "High", "Units"])


def build() -> Path:
    bridge, sens, mc = vm.build_all()
    b = bridge.set_index("scenario")

    md_title = f"""# Implications of the results

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; not published on Kaggle. Date-stamped 2026-10-19.

The competition entry is frozen at `c652424`. This notebook extends its logic — the three pricing mechanisms, the dollar value to one team, a low-political-cost adoption chunk, team fit, and messaging — and changes none of the judged artifacts.

**Every dollar figure here is an inference, not a measurement.** The measured coefficients are cited with their source files; the valuation assumptions are explicit and ranged. The base case is **${b.loc['Base','gross_m']:.1f}M gross per year**, **${b.loc['Base','net_m']:.1f}M net** after implementation cost, and **${b.loc['Base','ev_m']:.1f}M expected** at {vm.BASE.adoption_prob:.0%} adoption. The high case reaches $11M net; the low case is $0.9M net.
"""

    md_finding = """## The finding in one page

The entry's measured result is not "tracking predicts performance." It is that three pricing mechanisms see three different things:

| Mechanism | What it prices | Measured evidence |
|---|---|---|
| The stopwatch | Sacks, not pressure | The 40-yard dash and 10-yard split add nothing to pressure (joint p=0.998); out-of-sample pressure R² is −0.113 for the stopwatch and +0.178 for the 10 Hz burst. |
| The depth chart | Status and prior role | Next-season role: current role +0.606, draft capital +0.785, performance −0.011 (95% CI −0.119 to 0.097, n=233). Concurrent performance is −0.132 (p=0.031), marginal. |
| The cap | Performance, partly role | Full 909-player ledger: performance +0.328 (0.264–0.392); +0.143 (0.078–0.208) with playing time. |

The pure measurement finding: the 10 Hz burst predicts interior pressure at **+0.354 SD/SD** (0.143–0.565, n=64). Top versus bottom burst tercile pressure is **3.83% vs 2.47%** (+1.36 pp); sacks are **0.97% vs 0.35%** (2.7×). The signal is position-specific: DL +0.734, WR +0.366 (p=0.084), OL +0.058, TE +0.093; interaction p=0.0004.

Sources: `outputs/discovery/interior_burst_models.csv`, `interior_burst_validation.csv`, `interior_burst_players.parquet`, `role_allocation_coefficients.csv`, `outputs/salary/pay_model_full.csv`. The allocation gap is descriptive: late picks/UDFAs +0.59 SD, early picks −0.92 SD; the strict tail is 13 player-seasons (12 players). The group-mean decomposition is full 233: role spread 1.462 vs performance 0.046; reliable 192: 1.104 vs 0.106. The writeup's "nine parts" phrasing is not repeated here because it is not traceable to a single sample.
"""

    code_load = r"""
import base64, io, zlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def _load(b64):
    return pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(b64)).decode()))

bridge = _load("__BRIDGE__")
sens = _load("__SENS__")
mc = _load("__MC__")

display_bridge = bridge.copy()
display_bridge["share_of_cap"] = (display_bridge["share_of_cap"] * 100).round(1).astype(str) + "%"
print("Scenario table ($M/year):")
print(display_bridge.round(2).to_string(index=False))
""".replace("__BRIDGE__", _csv_b64(bridge)).replace(
        "__SENS__", _csv_b64(sens)
    ).replace("__MC__", _csv_b64(mc))

    assumptions = _assumptions_frame()
    code_assumptions = (
        "assumptions = pd.DataFrame("
        + repr([tuple(r) for r in assumptions.itertuples(index=False)])
        + ", columns="
        + repr(list(assumptions.columns))
        + ")\nprint(assumptions.to_string(index=False))"
    )

    md_model = f"""## The valuation model

Three routes, each an annual flow in $M:

- **Selection surplus** = hit-rate lift × (interior DL market value − rookie cost) × such picks per year. The four-year per-pick surplus is ${b.loc['Base','surplus_per_hit_4y_m']:.1f}M at base; at a {vm.BASE.hit_lift:.0%} hit-rate lift, the expected surplus is ${vm.BASE.hit_lift*b.loc['Base','surplus_per_hit_4y_m']:.1f}M per pick over four years. At {vm.BASE.picks_per_year:g} picks per year, the steady-state annual flow is **${b.loc['Base','selection_m']:.1f}M/year**.
- **Role reallocation** = cap saving per decision × decisions per cycle × reallocation efficiency = **${b.loc['Base','role_m']:.1f}M/year**.
- **Contract pricing** = contract portfolio × pricing correction = **${b.loc['Base','contract_m']:.1f}M/year**.

Gross is the sum; net subtracts the implementation cost; expected value multiplies net by the adoption probability. The routes are not causally additive: if the same organisational change drives both role and contract decisions, the low case is the conservative guide.
"""

    code_bridge = r"""
blue, orange, aqua = "#2a78d6", "#eb6834", "#1baf7a"
ink, secondary, surface, baseline = "#0b0b0b", "#52514e", "#fcfcfb", "#c3c2b7"

d = bridge.set_index("scenario").loc[["Low", "Base", "High"]]
fig, ax = plt.subplots(figsize=(8.8, 4.6))
x = np.arange(len(d))
bottom = np.zeros(len(d))
for col, color, label in [
    ("selection_m", blue, "Selection surplus"),
    ("role_m", orange, "Role reallocation"),
    ("contract_m", aqua, "Contract pricing"),
]:
    values = d[col].to_numpy()
    ax.bar(x, values, 0.56, bottom=bottom, color=color, label=label,
           edgecolor=surface, linewidth=1.5)
    for xi, value, base in zip(x, values, bottom):
        if value >= 1.2:
            ax.text(xi, base + value / 2, f"${value:.1f}M", ha="center",
                    va="center", fontsize=8, color="white")
    bottom += values
for xi, total in zip(x, bottom):
    ax.text(xi, total + 0.35, f"Gross ${total:.1f}M", ha="center",
            va="bottom", fontsize=9.5, fontweight="bold", color=ink)
ax.set_xticks(x)
ax.set_xticklabels(d.index)
ax.set_ylabel("$M per year")
ax.set_ylim(0, max(bottom) * 1.24)
ax.grid(axis="y", alpha=0.8)
ax.set_axisbelow(True)
ax.set_title("Value to one team: ~$6.6M gross/year at base", loc="left",
             fontsize=13, color=ink, pad=24)
ax.text(0, 1.045, "Base net $5.6M; EV $2.3M at 40% adoption. "
        "Dollar figures are inferences.", transform=ax.transAxes,
        fontsize=8.2, color=secondary, va="bottom")
ax.legend(loc="upper left", ncol=3, fontsize=8.5, handlelength=1.2)
fig.tight_layout()
plt.show()
"""

    md_sensitivity = f"""## Sensitivity

The largest driver is the **pricing correction** (a swing of ${sens.set_index('input').loc['pricing_correction','swing_m']:.1f}M/year between its low and high values), followed by the contract portfolio, role decisions, and the role-reallocation saving. The selection route is smaller: even at the high case it is ${b.loc['High','selection_m']:.1f}M/year, because the signal's hit-rate lift is applied to a late-pick surplus.

The Monte Carlo treats inputs as independent. Net value P10/P50/P90 is **${mc.set_index('metric').loc['net','p10_m']:.1f}M / ${mc.set_index('metric').loc['net','p50_m']:.1f}M / ${mc.set_index('metric').loc['net','p90_m']:.1f}M**; expected value is **${mc.set_index('metric').loc['expected_value','p10_m']:.1f}M / ${mc.set_index('metric').loc['expected_value','p50_m']:.1f}M / ${mc.set_index('metric').loc['expected_value','p90_m']:.1f}M**. The deterministic low/high is the wider stress range; the Monte Carlo is narrower because independent draws average out.
"""

    code_sensitivity = r"""
s = sens[sens["basis"].eq("net")].copy()
base_net = float(bridge.set_index("scenario").loc["Base", "net_m"])
s["low_delta"] = s["low_net_m"] - base_net
s["high_delta"] = s["high_net_m"] - base_net
print(s.sort_values("abs_swing_m", ascending=False)[
    ["label", "low_net_m", "high_net_m", "swing_m"]
].round(2).to_string(index=False))
s = s.sort_values("abs_swing_m", ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(9.0, 5.6))
y = np.arange(len(s))
ax.barh(y, s["low_delta"], color=orange, alpha=0.92, label="Low assumption", height=0.62)
ax.barh(y, s["high_delta"], color=blue, alpha=0.92, label="High assumption", height=0.62)
for yi, low, high, low_total, high_total in zip(
    y, s["low_delta"], s["high_delta"], s["low_net_m"], s["high_net_m"]
):
    if abs(high - low) < 0.6:
        ax.text(max(low, high) + 0.12, yi, f"≈${(low_total + high_total) / 2:.1f}M",
                ha="left", va="center", fontsize=7.5, color=secondary)
        continue
    if abs(low) > 0.05:
        ax.text(low - 0.12, yi, f"${low_total:.1f}M", ha="right",
                va="center", fontsize=7.5, color=secondary)
    if abs(high) > 0.05:
        ax.text(high + 0.12, yi, f"${high_total:.1f}M", ha="left",
                va="center", fontsize=7.5, color=secondary)
ax.axvline(0, color=baseline, lw=1.0)
ax.set_yticks(y)
ax.set_yticklabels(s["label"], fontsize=8.5)
ax.tick_params(axis="y", pad=8)
span = max(abs(s["low_delta"].min()), abs(s["high_delta"].max()))
ax.set_xlim(-span - 1.0, span + 1.0)
ax.set_xlabel("Change from the base net value ($M/year)")
ax.grid(axis="x", alpha=0.8)
ax.set_axisbelow(True)
ax.set_title("Which assumptions move the annual value most", loc="left",
             fontsize=13, color=ink, pad=24)
ax.text(0, 1.035, "Base net $5.6M/year; each input varied low/high with the others at base. "
        "Adoption is excluded (it scales expected value, not the net total).",
        transform=ax.transAxes, fontsize=8.5, color=secondary, va="bottom")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
          fontsize=8.5, handlelength=1.2)
fig.tight_layout()
plt.show()
"""

    code_mc = r"""
print("Monte Carlo summary ($M/year):")
print(mc.round(2).to_string(index=False))
"""

    md_zero = """## What would make it zero

| Lever | Breakeven | Base | Interpretation |
|---|---:|---:|---|
| Hit-rate lift | 0 pp | 15 pp | The selection surplus disappears. |
| Role saving per decision | $0 | $6M | Guarantees and dead money block the reallocation. |
| Pricing correction | 0% | 7.5% | The market already prices role-controlled performance. |
| Implementation cost | $6.6M | $1.0M | Cost consumes the gross value. |
| Adoption probability | 0% | 40% | No one acts on the analysis. |
| Contract coefficient | 0 | +0.143 | The 95% CI includes 0.078, so the true correction may be small. |

Zero is a scenario, not a forecast. The low case is the conservative guide if the routes overlap.
"""

    md_adoption = """## Adoption: a low-political-cost chunk

The chunk is not "fire the coach" or "reallocate every snap." It is:

1. Add the burst signal to the interior-DL draft board as one input alongside tape, college production, and draft slot.
2. In obvious pass-rush sub-packages, give a high-burst, low-cost interior lineman 10–15% more snaps and a low-burst, high-cap veteran 10–15% fewer. The veteran loses pass-rush snaps, not starting status or pay.
3. Price the next interior-DL contract on role-controlled performance (+0.143) rather than the raw performance coefficient (+0.328).

**Who loses:** the low-burst veteran loses snaps; the coach loses some discretionary authority; the incumbent scout loses the comfort of the stopwatch. That is why this is **Pareto-adjacent**, not strictly Pareto efficient.

Team archetypes (staffing as of 2026-10-19; source: Wikipedia's current NFL general manager and head coach lists; verify before quoting the table):

| Team | GM | Head coach | Why the structure fits | Caveat |
|---|---|---|---|---|
| Titans | Mike Borgonzi | Robert Saleh | New regime, defensive coach, rebuild, high draft capital; interior pressure is a live need. | GM and coach may be aligned, lowering the "challenge the coach" tension. |
| Browns | Andrew Berry | Todd Monken | Most analytics-native GM; cap reset; the cap-versus-role frame is directly salient. | Ownership and the Watson contract constrain a clean reallocation. |
| Jaguars | James Gladstone | Liam Coen | Young, analytics-forward regime with a draft-and-develop mandate. | Not a full rebuild; pressure to win now. |
| Falcons | Ian Cunningham | Kevin Stefanski | New regime; roster and cap reset; authority to re-price roles. | Both are new together, so the wedge is a design choice, not a live conflict. |
| Dolphins | Jon-Eric Sullivan | Jeff Hafley | New regime, defensive coach, clean slate. | The teardown may take precedence over fine-grained role allocation. |
| Cardinals | Monti Ossenfort | Mike LaFleur | Patient, draft-heavy GM; new coach; young roster. | The fit is structural, not a claim about personal analytics views. |

**First-mover caveat:** this is a transition rent, not a permanent edge. If every team adopts the principle, the market re-prices and the surplus flows to players. The window is plausibly 2–5 years.
"""

    md_messaging = """## Messaging

**The roof:** *The stopwatch is blind to pressure; the depth chart is blind to performance; the cap is not.*

**Three pillars:**

1. **Measurement.** The 10 Hz burst predicts interior pressure at +0.354 SD/SD (0.143–0.565, n=64); the 40 and 10-yard split add nothing (joint p=0.998; OOS −0.113 vs +0.178). The signal is position-specific: DL +0.734, OL/TE null; interaction p=0.0004.
2. **Allocation.** Next-season role: current role +0.606, draft +0.785, performance −0.011 (−0.119–0.097). The gap is +0.59 for late/UDFA and −0.92 for early picks; the group-mean decomposition is 31.7:1 role-to-performance in the full sample and 10.4:1 in the reliable sample.
3. **Value.** Base $6.6M gross / $5.6M net / $2.3M EV per year; range $0.9M–$11.1M net. It is a first-mover transition rent, not a permanent edge.

| Audience | Lead with | Do not lead with |
|---|---|---|
| Club analytics | Burst versus stopwatch, position-specific, out of sample. | The dollar figure or the "emperor" framing. |
| Cap / contract | Role-controlled +0.143 versus raw +0.328; exp≥4 +0.443/+0.217. | A promise of cap savings. |
| Coaching / personnel | Weekly stickiness (+0.753 role, −0.006 performance); the low-political-cost chunk. | "The depth chart is a status market." |
| League office | The rookie-scale and role-pipeline question. | Club-specific blame. |
| Analytics media | The three pricing mechanisms; "stopwatch blind to pressure." | The Tier 2 wedge as if it were identified. |
| General / portfolio | The tiers; measured versus inferred. | A single big number without a range. |

**Three lengths.**

- **One sentence:** the 10 Hz burst sees the pressure the stopwatch misses, the cap pays performance, the depth chart does not detectably, and the gap is mostly role.
- **Three sentences:** the burst predicts interior pressure where the stopwatch does not. The cap pays performance; next-season playing time follows prior role and draft status. The gap is mostly role, and the first team to reallocate the chunk captures a transition rent of roughly $5–6M a year, with a high case above $10M.
- **One paragraph:** the entry measures three pricing mechanisms. The stopwatch prices sacks, not pressure; the burst prices pressure, but only for interior defensive linemen. The depth chart prices status and prior role; its performance coefficient is −0.011. The cap prices performance at +0.328, or +0.143 with playing time. The gap is mostly role; under normal assumptions, the first team to act captures a transition rent, and the market re-prices once the principle is adopted.

**Objection handling.**

| Objection | Response |
|---|---|
| "The sample is small." | 64 interior player-seasons; the strict tail is 13. It is a screen, not a tool; the team-fixed-effects estimate is +0.298 (p=0.089). |
| "Coaches know more." | The claim is about information, not intelligence; performance is noisy, status is cheap. |
| "The cap already pays performance." | Yes: +0.328 raw, +0.143 with role. The gap is in playing time. |
| "This is sociology." | The Tier 0 result is football-specific; the structural reading is labelled. |
| "The number is made up." | It is an inference with an assumptions table, a range, and a zero case. |
| "Teams already do this." | Then the market is priced and the surplus is smaller. |

**What not to say.** No "proves coaches are biased"; no "Pareto efficient" without naming who loses; no "nine parts role to one part performance"; no "emperor has no clothes" in a club room; no promised savings; no causal claim; no raw data; no Kaggle publication during the competition.
"""

    md_not = """## What this is not

- Not a causal identification. The pressure and role results are associations; the agent model is model-reproduced.
- Not investment advice or a contract recommendation.
- Not a validated tool. The pressure sample is 64 interior player-seasons; the strict tail is 13 player-seasons.
- Not a redistribution of competition data. Only derived summary numbers appear here; the raw data is CC BY-NC 4.0 and is not copied.
- Not part of the judged entry. `writeup/`, `notebooks/02_final_public.ipynb`, and the Kaggle metadata are unchanged.
"""

    md_repro = """## Reproduce

```bash
python implications/code/value_model.py
python implications/code/figures.py
python implications/code/build_notebook.py
jupyter nbconvert --execute --to notebook --inplace implications/code/implications.ipynb
```

`value_model.py` writes the three CSV tables to `implications/outputs/` (gitignored). `figures.py` writes the two PNGs to `implications/writeups/figures/`. The notebook embeds the tables and runs without `implications/outputs/`.
"""

    nb = nbf.v4.new_notebook()
    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb["metadata"]["language_info"] = {"name": "python"}
    nb["cells"] = [
        nbf.v4.new_markdown_cell(md_title),
        nbf.v4.new_markdown_cell(md_finding),
        nbf.v4.new_code_cell(code_load),
        nbf.v4.new_markdown_cell(
            "### Assumptions\n\nAll dollar inputs are in $M/year unless noted. "
            "The measured coefficients are not assumptions; they are cited above."
        ),
        nbf.v4.new_code_cell(code_assumptions),
        nbf.v4.new_markdown_cell(md_model),
        nbf.v4.new_code_cell(code_bridge),
        nbf.v4.new_markdown_cell(md_sensitivity),
        nbf.v4.new_code_cell(code_sensitivity),
        nbf.v4.new_code_cell(code_mc),
        nbf.v4.new_markdown_cell(md_zero),
        nbf.v4.new_markdown_cell(md_adoption),
        nbf.v4.new_markdown_cell(md_messaging),
        nbf.v4.new_markdown_cell(md_not),
        nbf.v4.new_markdown_cell(md_repro),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, OUT)
    return OUT


if __name__ == "__main__":
    print(build())
