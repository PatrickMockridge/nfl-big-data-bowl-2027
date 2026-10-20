# Adversarial audit: the implied findings

**Status:** a GitHub-only extension. It is not part of the judged Big Data Bowl
entry, does not modify the artifacts frozen at `c652424`, and is not published
on Kaggle. Date-stamped **2026-10-20**.

**Contents:** [RED_BLUE.md](RED_BLUE.md) — the red/blue audit ·
[COOPTATION.md](COOPTATION.md) — external readings and insider threat ·
[scorecard.csv](scorecard.csv) — all 68 findings, one row each.

> **Audit only.** The public README and the extension writeups have not been
> changed. Where a verdict is *downgrade* or *concede*, the remediation register
> at the end of [RED_BLUE.md](RED_BLUE.md) records the recommended wording and
> the line it would replace. The public summaries therefore still carry the
> stronger claim. This document exists so the gap is visible, not so it can be
> hidden.

## Bottom line

The measured core survives. A 10 Hz burst is associated with interior
pressure; the cap is associated with measured performance; performance does not
detectably predict next-season role in the available measure. Those are real
results with real caveats.

The inferences built on that core are weaker than the public summaries. The
allocation gap is descriptive, not structural. The transfer template is not
established outside defensive line. The market portfolio is a scenario, not a
valuation, and its base is an arithmetic sum of non-additive routes. The
free-agency role premium is a conditional association, not an unearned premium;
its dollar value depends on judgment parameters, and the annual headline is not
haircut-adjusted.

The most serious problems are:

- the "nine parts role to one part performance" phrase, which the repo's own
  decomposition and messaging guide contradict;
- the "position-specific" wording, which the entry's own protocol says should
  be "concentrated in interior";
- the sack claim, whose outcome reliability is below the repo's own gate;
- the Tier 2 wedge, which is relabeled regressions rather than behavioral
  evidence;
- the uncut annual dollar headline;
- four different headline dollar numbers across four READMEs.

None of these makes the work worthless. Several make the public headline
stronger than the evidence. The co-optation risk in
[COOPTATION.md](COOPTATION.md) is real and independent of technical merit: the
work can be cited by labor, racial-justice, surveillance, safety, betting, and
antitrust critics, and insiders have identity, institutional, legal, and career
reasons to resist it.

## What counts as an implied finding

A finding is **implied** if it requires at least one step beyond a measured
association: a model, a counterfactual, a projection, a cross-population
extrapolation, an operational recommendation, or a normative reading. Direct
Tier 0 associations are audited only where an implied claim depends on them.
The audit covers the Tier 1–3 claims, the original implications report, the
transfer extension, the market portfolio, the free-agency deep dive, the
cross-cutting framing, and the non-empirical co-optation readings. Code
correctness and the raw data pipeline are out of scope, except where a
code-versus-label discrepancy is load-bearing.

## How to read a verdict

| Verdict | Meaning |
|---|---|
| **Survives** | The attack fails; the finding stands as stated. |
| **Survives with label** | The finding stands only with a named qualifier: tier, sample, CI, non-causal. If the label does not travel, treat it as a downgrade. |
| **Downgrade** | The public claim must be weakened; a narrower claim may stand. |
| **Concede** | The attack succeeds; withdraw the claim from the public summary. |
| **Unresolved** | Current data cannot settle it; the entry names the test. |
| **Out of scope** | Normative or political, not an empirical finding. |

**Red severity:** *critical* (could invalidate the headline); *high* (changes the
headline or a major number); *medium* (changes a secondary claim); *low*
(wording/optics). **Blue strength:** *strong* (the repo already answers with
evidence); *moderate* (partial answer; caveat needed); *weak* (attack lands);
*none* (concede).

## Summary

| Family | Findings | Critical | Downgrade or concede | Unresolved |
|---|---:|---:|---:|---:|
| J — judged entry | 12 | 2 | 7 | 0 |
| I — original implications | 6 | 1 | 5 | 1 |
| T — transfer | 9 | 0 | 3 | 0 |
| M — market portfolio | 9 | 1 | 3 | 1 |
| F — free agency | 19 | 3 | 4 | 1 |
| X — cross-cutting | 13 | 2 | 9 | 1 |
| **Total** | **68** | **9** | **31** | **4** |

Verdict distribution: 5 survive, 26 survive with label, 26 downgrade, 5 concede,
4 unresolved, 2 out of scope. The skew toward "survives with label" is the
finding: the repo already labels most of its claims, but the labels do not
travel to the headline.

**Read by scope.** The verdicts are not equally important. The public headline
depends on a small set: F10/F11 (the uncut annual dollar), J1–J4 (the pressure
and position-specificity claims), X1 (the "does not reward" wording), and X9
(the four headline numbers). A downgrade on a supporting claim — I2, I5, M5,
M7, or X5 — weakens the package but does not invalidate the measured core. The
measured core survives on its own.

## The ten most dangerous findings

1. **The annual headline is not haircut-adjusted** (F10/F11). The $6.05M net is
   the uncut premium minus $1M. At the base 0.40 haircut, the annual capture is
   about $2.8M gross / $1.8M net.
2. **"Nine parts role" is contradicted by the repo's own decomposition and
   banned by its own messaging guide** (J9).
3. **"Position-specific" fails the entry's own go/no-go** (J4). EDGE pressure
   p=0.036, interaction p=0.137; the protocol says "concentrated in interior."
4. **The headline analyses were added after preregistration; the preregistered
   novelty failed** (X10/X11).
5. **The pressure claim is cross-sectional, not predictive** (J1). Temporal R²
   is −0.045; team-FE CI crosses zero; the title says "real."
6. **Sacks fail the repo's own reliability gate** (J2). Split-half Spearman–
   Brown 0.493; the stopwatch is the stronger out-of-sample sack model.
7. **The Tier 2 wedge is relabeled regressions** (J10/J11). The "GM weight" is
   the cap coefficient; the coach shuffle is p=0.10; the wedge has no
   uncertainty.
8. **Four different headline dollar numbers** (X9). $6.6M, $24.9M, $7.05M, and
   $11.03M in four READMEs.
9. **The allocation and contract levers are substitutes, not additive** (M4/X8).
   The base $11.03M assumes independence; the low case is −$0.68M.
10. **Co-optation and insider threat** (X12, [COOPTATION.md](COOPTATION.md)).
    The work arms external critiques and gives insiders reasons to reject it
    regardless of merit.

## What survives

| Claim | Verdict | The label that must travel |
|---|---|---|
| Burst → interior pressure (+0.354) | Survives with label | Cross-player scouting association; temporal R² negative; team-FE CI crosses zero. |
| Cap → performance (+0.328 raw) | Survives with label | Cap charge, not pay; performance measure is role-loaded. |
| Depth-chart null (−0.011) | Survives with label | Absence of evidence in this measure; not proof of zero. |
| 2026 APY gap (+0.179) | Survives with label | Conditional association in one class; not unearned role; not causal. |
| 2025 cap gap (+0.185) | Survives with label | Cap hit, not APY or cash. |
| Draft-matched gap (+0.151) | Survives with label | Smaller; still model-dependent. |
| Transfer nulls (TE/OL/DB) | Survives | Unidentifiable for measurement reasons, not no effect. |
| Portfolio low case (−$0.68M) | Survives (as disclosure) | The honest stress case; the headline total is still a downgrade. |
| Tier discipline | Survives | The repo separates measured, descriptive, inferred, and normative claims. |

## Read this in order

1. [RED_BLUE.md](RED_BLUE.md) — rules, claim genealogy, global briefs, and the
   68 finding entries.
2. [COOPTATION.md](COOPTATION.md) — how external critics read the work and why
   insiders resist it.
3. [scorecard.csv](scorecard.csv) — the machine-readable summary.

## What would change this audit

- A 2026 holdout and a team-FE model with adequate power for the burst claim.
- An errors-in-variables correction and an expected-role control for the role
  premium.
- A pre-specified interaction with a clean EDGE placebo for position
  specificity.
- A reconciled annual dollar headline with the haircut applied consistently.
- A joint adoption model for the portfolio.
- A single sample audit table for the count inconsistencies.

Until then, the verdicts stand.
