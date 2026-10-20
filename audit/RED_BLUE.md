# Red team / blue team: an adversarial audit of the implied findings

**Status:** a GitHub-only extension. It is not part of the judged Big Data Bowl
entry, does not modify the artifacts frozen at `c652424`, and is not published
on Kaggle. Date-stamped **2026-10-20**.

**Companions:** [README](README.md) · [COOPTATION](COOPTATION.md) ·
[scorecard.csv](scorecard.csv).

> **Audit only.** The public README and the extension writeups have not been
> changed. Where a verdict is *downgrade* or *concede*, the remediation
> register at the end records the recommended wording and the line it would
> replace. The public summaries therefore still carry the stronger claim. This
> document exists so the gap is visible, not so it can be hidden.

## 0. Rules of engagement

1. The red team attacks the **claim**, not the author, and uses the strongest
   version of the objection, not a strawman.
2. The blue team may not retreat to "we already said association." It must
   answer the attack as a reader would encounter the claim.
3. The blue team concedes when the attack lands. An audit in which everything
   survives is not an audit.
4. Every number traces to a committed file, or to a named regeneration command.
   `outputs/` is gitignored; where a number exists only there, the entry says so.
5. Empirical attack and normative/political reading are separated. A political
   reading is not a statistical finding, and a statistical finding does not
   settle a political argument.
6. A verdict is about the claim **as stated at the cited line**, not about the
   underlying data set.
7. *Survives with label* means the label must travel. A summary that drops the
   label is a downgrade, whatever this document says.

**Scope.** A finding is *implied* if it requires at least one step beyond a
measured association: a model, a counterfactual, a projection, a
cross-population extrapolation, an operational recommendation, or a normative
reading. Direct Tier 0 associations are audited only where an implied claim
depends on them. Code correctness and the raw data pipeline are out of scope,
except where a code-versus-label discrepancy is load-bearing.

## 1. Claim genealogy

The final headline is not the preregistered headline. This is the sequence, with
the dates the repo records:

| Date | Artifact | Primary claim | Status |
|---|---|---|---|
| 2026-10-18 | `docs/PREREGISTRATION.md` | Yellow/Möbius transition-zone framework; `player_get_off` primary; pressure/sacks secondary; 2025 confirmatory | Pre-registered |
| 2026-10-18 | `docs/PREREGISTRATION_v2.md` | Broadened test = rookie pond step-up; role-allocation, Combine-movement, and salary analyses added after the preregistered tests | Exploratory |
| 2026-10-19 | `docs/INTERIOR_BURST_PROTOCOL.md` | Burst pressure/sacks as the drill-translation entry; conditional go; position specificity fails; pressure is cross-sectional | Exploratory, protocol frozen |
| 2026-10-19 | `docs/AGENT_MODEL_PROTOCOL.md` | Two-agent allocation model as Tier 2 support | Model-reproduced |
| 2026-10-20 | `implications/` | One-team dollar model: $6.6M gross / $5.6M net / $2.3M EV | Inference |
| 2026-10-20 | `implications/markets/` | Top-down portfolio $24.9M, then bottom-up override $11.03M total | Inference |
| 2026-10-20 | `implications/free_agency/` | Bottom-up role premium $7.05M uncut / $1.82M capture net | Inference |
| 2026-10-20 | `README.md` | Headline moves to the free-agent role premium | Inference |

The preregistered novelty check said public notebooks already cover DL bend,
burst, and pass-rush kinematics; the entry's claimed contribution was the
Yellow/Möbius framework (`docs/gate_decision.md:45`). That framework returned a
wide null. The final entry's two headline claims — the burst and the allocation
gap — were both added after the preregistered tests (`docs/PREREGISTRATION_v2.md:90-92`;
`docs/INTERIOR_BURST_PROTOCOL.md:3`). The repo says this in pieces. The
headline does not say it at all. That is the single most important procedural
fact in this audit.

## 2. Global red brief: the case against the work

**R1. The inferential chain is longer than the evidence.** The measured objects
are narrow: a burst-pressure association in 64 interior player-seasons, a
cap-performance association in 909 players, and a null next-role coefficient in
233 player-seasons. The claims built on them are much larger: the depth chart is
status-driven, the allocation gap is the lever, the market misprices role, and a
median team can capture about $6M a year. Each link adds an assumption. The
final dollar has at least five judgment parameters. A reader is asked to accept
the chain because the first link is solid.

**R2. The central construct is not identified.** "Role" is playing time. Playing
time is produced by performance, trust, health, scheme, assignment difficulty,
and coaching. Controlling for role and calling the residual "pay for role beyond
performance" is a mediation claim without identification. The model cannot
distinguish *unearned role* from *unmeasured productivity*. The repo concedes
that `snap_share` is endogenous (`implications/free_agency/writeups/02_pricing.md:112-115`),
but the public headline does not carry the concession.

**R3. Measurement error can manufacture the result.** `perf_z` is a shrunk,
noisy composite. `snap_share` is close to mechanical and highly reliable.
Classical measurement error in performance biases its coefficient toward zero;
adding a reliable role variable absorbs variance for reliability reasons alone.
The role premium is not disattenuated. A result that is partly a reliability
artifact is being read as a market fact.

**R4. The dollar is a scenario, not an estimate.** The 0.40 haircut is
inherited, not estimated. The $1M implementation cost is a plug. The 40%
adoption rate is a judgment. The annual headline is not haircut-adjusted. The
premium is concentrated in the top decile. The contract population is one
signing class. The saving is a counterfactual, not observed cash. A point
estimate with five free parameters is a scenario.

**R5. The transfer is a template, not a structure.** The transfer extension
tests one benchmark (the entry's own signal), one task-matched DL signal that is
Holm-marginal with negative incremental R² for interior, one weak WR result, and
three unidentifiable positions. "The structure travels" is a claim about a way
of looking, not about a replicated structure. The allocation-gap transfer rests
on 233 player-seasons and strict tails of 4–6 players.

**R6. The portfolio is not additive.** The allocation and contract levers share
the same role construct. The base $11.03M assumes independence. The low case is
−$0.68M. The "conservative" column is base position markets plus a CI-zeroed
contract market; it is not a portfolio-wide conservative view. The EV is the
same arithmetic sum multiplied by 0.40. The portfolio is an accounting
convention, not an economic model.

**R7. The recommendations are untested.** "Actionable" means plausible. There is
no pilot, no out-of-sample adoption, no team-level experiment, and no test of
whether a club can actually reallocate snaps or reprice a renewal wave. The
cap-manager playbook is a hypothesis.

**R8. The framing is normative.** "The depth chart does not reward performance"
is an indictment, not a measurement. "Price the role" is a recommendation.
"The market is inefficient" assumes the model is right. The work is careful in
its limits sections and much less careful in its titles, headlines, and
one-sentence summaries. The normative frame is what travels.

**R9. The claim drifted after preregistration.** The preregistered contribution
failed. The final contribution was assembled after the data were seen, labeled
exploratory in the protocols, and then made the public headline. The repo is
unusually honest about the sequence, but the headline is not.

**R10. The work is co-optable and procedurally exposed.** External critics can
cite the allocation gap for a labor critique, the Combine for a surveillance
critique, the role premium for a pay-cut critique, and the player-level outputs
for a betting critique. Insiders have identity, institutional, legal, and career
reasons to reject the work regardless of its technical merit. The post-deadline
README churn and the public discussion thread add procedural surface. See
[COOPTATION.md](COOPTATION.md).

## 3. Global blue brief: the case for the work

**B1. The tiers are explicit.** The repo separates measured, descriptive,
model-reproduced, inferred, and normative claims, and attaches a source to each.
That is more discipline than most competition entries.

**B2. The weakening cross-checks are reported.** The 2025 APY cross-check is
+0.105 with a CI crossing zero; the 2024 sample is null; the team-FE gap is
+0.099 with a CI crossing zero; the draft-matched gap shrinks to +0.151. The
repo prints all of them next to the headline estimate.

**B3. The bottom-up valuation corrects the top-down number.** The earlier $24.9M
was a synthetic upper-tail portfolio. The dedicated report replaces it with the
actual 2026 signing class and shows the bridge. The correction is the point.

**B4. The transfer screen reports nulls and unidentifiable areas.** TE, OL, and
DB are labeled unidentifiable rather than null. WR is labeled weak. The task-
matched DL signal is reported next to the benchmark, with the Holm correction
and the negative incremental R². The extension does not force a universal story.

**B5. The portfolio reports a negative low case.** The low case is −$0.68M. The
repo does not hide the possibility that the combined levers destroy value.

**B6. The measured core is robust in-sample.** The burst-pressure association is
+0.354 with a CI excluding zero and survives role controls (+0.362). The
cap-performance association is +0.328 with a CI excluding zero in 909 players.
The drill-translation contrast (stopwatch versus burst) is the strongest result
in the repo.

**B7. The code and protocols are transparent.** The models, seeds, gates, and
failure criteria are in the repository. The protocols were frozen before the
final runs. The audit can trace every number.

**B8. The work is falsifiable.** The protocols name the tests that would
overturn the claims. This audit adds more. A claim that can be tested is worth
more than a claim that cannot.

**B9. The value is diagnostic, not predictive.** The work identifies where to
look — the depth chart, the role premium, the transfer template — not what will
happen. The repo says this repeatedly.

**B10. The judged artifacts are frozen and the extensions are labeled.** The
entry is at `c652424`; the extensions say they are not part of it. The work does
not retroactively change the judged artifact.

## 4. Finding audit

### J — Judged entry

#### J1. Burst predicts interior pressure

**Claim.** "The burst predicts pressure at +0.354 SD per SD (95% CI 0.143 to
0.565, n=64)" — `writeup/submission.md:11`.
**Tier.** Measured association.
**Red.** The estimate is cross-player, not temporal. The 2025 temporal R² is
−0.045; the team-fixed-effects estimate is +0.298 with a CI from −0.045 to 0.640
(`docs/INTERIOR_BURST_PROTOCOL.md:167`). The title says the signal is "real," but
the repo's own validation section says the association "is not robust enough to
call a validated tool" (`implications/writeups/00_thesis.md:47`). A reader who
sees only the title will overread a cross-sectional screen as a forecast.
**Blue.** The in-sample association is strong, survives role controls (+0.362,
0.172–0.552), and the drill-translation contrast is the cleanest result in the
repo: the stopwatch's pressure OOF R² is −0.113 and the burst's is +0.178. The
protocol explicitly labels the claim cross-player and conditional-go.
**Verdict.** Survives with label: "cross-player scouting association, not a
season forecast; team-FE CI includes zero." **Residual risk:** High.
**What would settle it.** A 2026 holdout and a team-FE model with adequate
power.

#### J2. Burst predicts sacks

**Claim.** "sacks at +0.317 (0.083 to 0.550, n=63)" — `writeup/submission.md:11`.
**Tier.** Measured association.
**Red.** The interior sack outcome has split-half Spearman–Brown reliability
0.493, below the repo's own 0.50 gate (`docs/INTERIOR_BURST_PROTOCOL.md:159`).
The stopwatch is the stronger out-of-sample sack model (OOF R² +0.120 versus
+0.059 for the burst), and the burst adds only +0.007 R² over traditional
timing. The sack claim is the weaker half dressed as the stronger one.
**Blue.** The sack coefficient is positive in-sample and temporally (+0.182),
and the protocol calls sacks the robustness anchor, not a tracking-unique
finding. The entry says the stopwatch sees sacks.
**Verdict.** Downgrade: "sacks are consistent with the burst, but the stopwatch
is the stronger sack model and the outcome is below the reliability gate."
**Residual risk:** High.
**What would settle it.** A prospective season with outcome reliability ≥0.50.

#### J3. The stopwatch is blind to pressure

**Claim.** "The stopwatch is blind to pressure" — `writeup/submission.md:13`.
**Tier.** Measured null.
**Red.** A joint p=0.998 is a failure to detect, not proof of blindness. The repo
applies "absence of evidence, not proof of zero" to the depth chart
(`writeup/submission.md:25`) but not to the stopwatch. The asymmetry is
rhetorical: one null is hedged, the other is promoted to a property.
**Blue.** The out-of-sample contrast is strong: the stopwatch's pressure OOF R²
is −0.113 and the burst's is +0.178. The joint test is not the only evidence.
**Verdict.** Downgrade: "the stopwatch does not carry the pressure signal in
this sample," not "blind." **Residual risk:** Medium.
**What would settle it.** An equivalence test with a pre-specified margin.

#### J4. The Combine signal is position-specific

**Claim.** "The Combine signal is position-specific" — `writeup/submission.md:17`.
**Tier.** Measured/inferred.
**Red.** The entry's own protocol records a failed go/no-go: EDGE pressure
p=0.036, where the pre-specified threshold was "not significant at 0.05"; the
interaction is p=0.137; the protocol says the correct wording is "concentrated
in interior linemen (2.3× the edge coefficient)," not "position-specific"
(`docs/INTERIOR_BURST_PROTOCOL.md:182-204`). The submission uses the stronger
phrase. The p=0.0004 interaction belongs to a different model (Combine movement
→ position-specific performance), and the reader will conflate the two.
**Blue.** The Combine-movement interaction is genuinely p=0.0004 for the
performance outcome, and the submission reports the EDGE coefficient (+0.157)
next to the interior coefficient. The position-specific estimates are labeled
exploratory.
**Verdict.** Downgrade: "concentrated in interior linemen; the burst-pressure
interaction is not significant, and the two interaction tests must be
distinguished." **Residual risk:** Critical.
**What would settle it.** A pre-specified interaction with adequate power and a
clean EDGE placebo.

#### J5. Combine-performance interaction p=0.0004

**Claim.** "interaction p=0.0004" — `writeup/submission.md:17`.
**Tier.** Measured.
**Red.** The interaction is for the Combine-movement composite and the
position-specific performance outcome, not for the burst-pressure model. The
submission's sentence moves from the burst to the Combine composite without
flagging the switch. The p=0.0004 is real for the model it belongs to; it is not
evidence for the burst claim.
**Blue.** The submission reports the per-position coefficients and the
interaction in the same sentence; the table gives the model. The distinction is
visible to a careful reader.
**Verdict.** Survives with label: "the interaction applies to the Combine-
movement performance model, not the burst-pressure model." **Residual risk:**
Medium.
**What would settle it.** Separate the two interaction tests in the public
summary.

#### J6. The cap pays performance

**Claim.** "a standard deviation of measured performance is associated with
+0.328 log points of cap charge (95% CI 0.264 to 0.392)" — `writeup/submission.md:21`.
**Tier.** Measured association.
**Red.** The performance measure is nflverse production, which is partly
role-loaded (r≈0.5 with snaps); the cap number is an accounting residual, not
pay; the sample covers 68.7% of active-cap dollars and excludes offensive
linemen and specialists. The prose says "pays for performance," which implies
intent. The repo's own caveat says "cap spending is an estimate, not intent"
(`writeup/submission.md:61`).
**Blue.** The association is large, precise, and survives adding role (+0.143,
0.078–0.208). It is the strongest salary result in the repo. The caveats are in
the same paragraph and the limits section.
**Verdict.** Survives with label: "cap charge is associated with measured
production, partly through role; this is not a causal pay-for-performance
estimate." **Residual risk:** High.
**What would settle it.** A role-free performance measure and a cash model.

#### J7. The depth chart does not detectably reward performance

**Claim.** "the performance coefficient is −0.011 (95% CI −0.119 to 0.097,
n=233)" — `writeup/submission.md:25`.
**Tier.** Measured null.
**Red.** The CI rules out only large effects; a modest positive effect is
compatible with the data. The concurrent estimate is −0.132 (p=0.031), the
within-player estimate is −0.095 (p=0.11), and the shuffle variant is −0.10.
The performance measure is an NGS residual that does not capture assignment
difficulty, double teams, communication, or trust — the things coaches actually
use to allocate snaps. The null may be a measurement gap, not a coaching
pattern.
**Blue.** The next-season model has out-of-sample R² 0.503, and the performance
coefficient stays between −0.038 and +0.026 across folds. Current role (+0.606)
and draft (+0.785) are strong. The entry says "absence of evidence, not proof of
zero."
**Verdict.** Survives with label: "no detectable association in this measure and
sample; not proof that performance is unrewarded." **Residual risk:** High.
**What would settle it.** An assignment-aware performance measure and a larger
role sample.

#### J8. Allocation gap +0.59 late / −0.92 early

**Claim.** "The performance-role gap by draft is +0.59 for late picks and
undrafted players and −0.92 for early picks in the full 233-row sample" —
`writeup/submission.md:31`.
**Tier.** Descriptive decomposition.
**Red.** The gap is a constructed difference between two standardized measures;
it is not a behavioral quantity. The strict top/bottom quartile tail is 13
player-seasons (12 players), and the appendix gives 11 players. Most
per-quartile cells in the transfer extension have CIs crossing zero. The
"gap" is mostly the role spread (1.462 SD) versus a tiny performance spread
(0.046 SD); that is a statement about how little performance varies after
standardization, not necessarily about misallocation.
**Blue.** The pattern is consistent across the full and reliable samples, and
the transfer extension finds the same sign in WR, OL, and DL. The repo labels it
descriptive, not causal.
**Verdict.** Survives with label: "descriptive gap in this measure; the tails
are a review list, not a population." **Residual risk:** High.
**What would settle it.** An independent role measure and a strict-tail
replication.

#### J9. Nine parts role to one part performance

**Claim.** "The gap is about nine parts role to one part performance" —
`writeup/submission.md:31`.
**Tier.** Implied ratio.
**Red.** The source decomposition is 1.462/0.046 = 31.7:1 in the full sample and
1.104/0.106 = 10.4:1 in the reliable sample (`implications/writeups/00_thesis.md:33`).
Neither is 9:1. The repo's own messaging guide bans the phrase as "not traceable
to one sample" (`implications/writeups/03_messaging.md:68`). The judged entry
prints it anyway. This is the clearest internal contradiction in the repo.
**Blue.** None. The number cannot be defended.
**Verdict.** Concede: withdraw the phrase. **Residual risk:** Critical.
**What would settle it.** Nothing; use the two decompositions with their samples.

#### J10. The agent wedge

**Claim.** "The coach weights performance at −0.13 … the GM at +0.14. The wedge
is +0.28" — `writeup/submission.md:39`.
**Tier.** Model-reproduced, not identified.
**Red.** The "GM weight" is the measured cap-with-role coefficient (n=908), not
a separate behavioral parameter; the coach weight is the concurrent-role
coefficient, whose shuffle variant is −0.10 (p=0.10). The wedge is a difference
of two point estimates from different measures (NGS residual versus nflverse
production), with no propagated uncertainty. The model calibrates to the
regressions and then reports the calibration as a behavioral finding. It adds
no evidence beyond the regressions.
**Blue.** The protocol freezes calibration and validation moments separately,
states failure criteria, and labels the model "model-reproduced, not identified"
wherever it appears. The validation moments (allocation gap, strict tail, cap
with role, monotonicity, negative control) are genuine checks.
**Verdict.** Downgrade: "the regressions imply a cross-construct difference of
about 0.28; this is not a behavioral weight." **Residual risk:** High.
**What would settle it.** Behavioral data on coaching decisions and uncertainty
propagation through the wedge.

#### J11. Simulated role uplift

**Claim.** "raises the top-performance group's role by 0.32 SD and the strict
tail's role by 0.33 SD in the model" — `writeup/submission.md:39`.
**Tier.** Model-reproduced.
**Red.** The numbers are deterministic output of a model built on the
assumption being tested. There is no CI, no stochastic simulation, and no
external validation. Two decimal places imply a precision the model does not
have.
**Blue.** The sentence says "in the model" and "model-reproduced, not
identified." The protocol says the model is one paragraph, one figure, one
notebook cell.
**Verdict.** Downgrade: report as a model scenario without decimal precision.
**Residual risk:** Medium.
**What would settle it.** A stochastic simulation with CIs and a pilot.

#### J12. Tier 3 recommendations and scorecard usability

**Claim.** The coach review, GM Combine use, league-office structural reading,
youth development target, and the scorecard's "week-to-week usability" —
`writeup/submission.md:43-61`.
**Tier.** Perspective/normative.
**Red.** "Usability" is supplied by "principle," not by the weekly data, which
is exploratory. The coach review has no tested cadence. The GM recommendation
uses a position-specific Combine result that is cross-player and conditional.
The league-office claim that "the gap is structural" is not identified. The
scorecard's "uniqueness" row is contradicted by the gate decision's novelty
check, which says public notebooks already cover DL burst.
**Blue.** The scorecard marks the evidence tier and the caveats in each row. The
recommendations are labeled perspectives, not findings.
**Verdict.** Downgrade: call them hypotheses or perspectives, not operational
claims. **Residual risk:** Medium.
**What would settle it.** A pilot with a pre-specified cadence and outcome.

### I — Original implications report

#### I1. One team: $6.6M gross / $5.6M net / $2.3M expected

**Claim.** "the base case is $6.6M gross per year, $5.6M net after
implementation cost, and $2.3M expected at 40% adoption" —
`implications/README.md:7`.
**Tier.** Inference.
**Red.** The model has more than a dozen judgment parameters, and the route that
uses the Combine signal — selection — contributes only $0.79M of the $6.64M
gross (`implications/writeups/01_valuation.md:42-48`). The contract route
($3.75M) is the contested role premium; the role route ($2.10M) is the same
construct seen another way. The routes are not additive. The 40% adoption rate,
the $1M implementation cost, the hit-rate lift, the reallocation efficiency, and
the contract portfolio are all judgments. The Monte Carlo does not model the
probability that the signal itself fails. The headline is a scenario bundle, and
the unique measurement contributes about 12% of it.
**Blue.** Every assumption is in a table with low/base/high values; the
sensitivity shows the pricing correction and contract portfolio dominate; the
report says "the number is not a forecast"; the selection route is deliberately
small; the low case is $0.9M net; the $6.6M break-even cost is reported.
**Verdict.** Downgrade: report the route decomposition in the headline and call
the total a scenario, not a value. **Residual risk:** Critical.
**What would settle it.** An independent cost/benefit study or a club pilot with
observed reallocation and contract outcomes.

#### I2. The three routes are additive

**Claim.** The base scenario sums selection $0.79M + role $2.10M + contract
$3.75M = $6.64M gross — `implications/writeups/01_valuation.md:58-66`.
**Tier.** Inference.
**Red.** The report itself says "the routes are not causally additive" and "the
selection, role, and contract routes can be the same organisational decision
seen three ways" (`implications/writeups/01_valuation.md:66,104`). The headline
still presents the sum. The overlap is not an edge case; it is the central
economic question.
**Blue.** The report states the caveat twice and says the low case is the
conservative guide.
**Verdict.** Concede the headline sum; use the low case as the one-change
number. **Residual risk:** High.
**What would settle it.** A joint adoption model with explicit overlap.

#### I3. Pareto-adjacent and politically manageable

**Claim.** "the losses are small, concentrated, and politically manageable
relative to the gain" — `implications/writeups/02_adoption.md:13`;
"Pareto-adjacent" — `implications/writeups/03_messaging.md:67`.
**Tier.** Normative.
**Red.** "Small" and "politically manageable" are unquantified. The losers are
the incumbent player and agent whose price is repriced; the co-optation annex
shows the finding is politically radioactive, not manageable. No evidence
supports the political judgment.
**Blue.** The report says "Pareto-adjacent," not "Pareto efficient," and
explicitly names the loser. That is more honest than most.
**Verdict.** Concede "politically manageable"; keep "Pareto-adjacent" only with
the named loser. **Residual risk:** High.
**What would settle it.** None; it is a normative claim.

#### I4. The first-mover window is 2–5 years

**Claim.** "The value is a transition rent, plausibly 2–5 years, not a permanent
edge" — `implications/writeups/01_valuation.md:105`.
**Tier.** Inference.
**Red.** There is no data on adoption timing. The window is a guess. The report
also says that if every team adopts, the market reprices and the surplus flows
to players — which means the dollar case is self-limiting by construction.
**Blue.** The report labels it "plausibly" and treats it as a transition rent,
not a permanent edge.
**Verdict.** Unresolved. **Residual risk:** Medium.
**What would settle it.** Adoption timing data or a club-by-club contract
review.

#### I5. The market does not price the signal

**Claim.** "The market does not price the signal that predicts pressure" —
`implications/writeups/00_thesis.md:37`.
**Tier.** Inference from a null correlation.
**Red.** The evidence is a null correlation between burst and draft capital:
+0.034, 95% CI −0.044 to 0.111. A null is not "unpriced." The CI includes a
moderate positive correlation. Draft capital is a proxy for the market's belief,
not a price. The transfer protocol's "unpriced" label is a convention (|ρ|<0.20),
not an estimate of pricing.
**Blue.** The point estimate is near zero, and the same method detects the
40-yard dash's pricing in WR (ρ=0.335), DB (ρ=0.398), and OL (ρ=0.266). The
writeup calls it a descriptive association, not a claim that teams ignore the
drill.
**Verdict.** Downgrade: "no detectable correlation with draft capital in this
sample," not "the market does not price it." **Residual risk:** High.
**What would settle it.** An equivalence test and direct draft-board or
contract-price data.

#### I6. The depth chart suppresses the players who have it

**Claim.** "the depth chart then suppresses the players who have it" —
`implications/writeups/00_thesis.md:37`.
**Tier.** Causal/normative.
**Red.** "Suppresses" implies intent and a causal mechanism. The evidence is a
null next-role coefficient and a descriptive gap. The coach may be weighting
unmeasured performance, health, or assignment difficulty. The report says the
coach is "not foolish," but the verb does the opposite work.
**Blue.** The thesis says "a structural claim, not a moral one" and explains the
coach's risk aversion.
**Verdict.** Downgrade: "the allocation pattern is consistent with role
persistence," not "suppression." **Residual risk:** High.
**What would settle it.** An identification strategy for coaching decisions.

### T — Transfer extension

#### T1. The structure travels; the measurement does not

**Claim.** "The structure of the entry's argument travels. The measurement does
not" — `transfer/README.md:16-31`.
**Tier.** Descriptive.
**Red.** The "structure" is a template the author applies; the evidence is one
benchmark, one task-matched DL signal that is Holm-marginal with negative
incremental R² for interior, one weak WR result, and three unidentifiable
positions. "Travels" is too strong for a pattern that is tested in one position
and weakly in another.
**Blue.** The extension is explicit about what travels, reports the nulls, says
"the answer is uneven, and that is the point," and carries no dollar model.
**Verdict.** Survives with label: "the template can be applied; the measurement
transfer is not established." **Residual risk:** Medium.
**What would settle it.** More positions with reliable outcomes.

#### T2. The DL benchmark reproduces the entry

**Claim.** "`burst_z` → pressure is +0.368 (95% CI 0.149 to 0.587, n=64),
against the entry's +0.354 (0.143 to 0.565)" — `transfer/README.md:21-23`.
**Tier.** Measured.
**Red.** This is the entry's own signal re-run, not a transfer. It differs by
0.014 and is not run with identical controls. A reader who skims the README will
anchor on +0.368 and conclude the DL drill transfers, which the next table
denies.
**Blue.** The README labels it the "DL positive control" and says it reproduces
the entry; the task-matched signal is in the next bullet.
**Verdict.** Survives with label: "benchmark, not transfer." **Residual risk:**
Medium.
**What would settle it.** Identical controls across the benchmark and the
transfer model.

#### T3. The task-matched DL signal

**Claim.** "The task-matched pass-rush signal adds −0.027 for interior and
+0.015 for edge" — `transfer/writeups/01_drill_translation.md:47-53`.
**Tier.** Measured.
**Red.** The interior coefficient is +0.271 with a CI from 0.025 to 0.517,
barely above zero; the Holm-corrected p is 0.061. The edge coefficient is +0.166
with Holm p=0.054. The interior incremental R² is negative. The positive
coefficient is conditional on draft. The out-of-sample increment over the
stopwatch is not established.
**Blue.** The writeup reports both unadjusted and Holm, calls the incremental
check "sobering," and says the positive coefficient is conditional on draft.
**Verdict.** Survives with label: "positive but Holm-marginal; no OOS increment
for interior." **Residual risk:** High.
**What would settle it.** A larger sample and a Holm-corrected replication.

#### T4. The "supported" status

**Claim.** The drill-translation table marks both DL rows "supported" —
`transfer/writeups/01_drill_translation.md:30-33`.
**Tier.** Label.
**Red.** The status is unadjusted. The pre-registered Holm correction makes both
rows non-significant at 0.05 (p=0.061/0.054). The link-matrix figure colors them
green. A reader who sees the table or figure will conclude "supported" without
reading the footnote.
**Blue.** The writeup says "the unadjusted status is supported, the corrected
result is borderline."
**Verdict.** Downgrade: the status column should say "borderline after Holm."
**Residual risk:** High.
**What would settle it.** Report the corrected status first.

#### T5. WR is weak

**Claim.** "+0.053 (−0.174, 0.280), 149 rows/82 players … weak" —
`transfer/writeups/01_drill_translation.md:27`.
**Tier.** Measured.
**Red.** "Weak" can be read as null. The CI spans zero and the rank correlation
is 0.003. WR is the only testable non-DL area, so the transfer evidence outside
DL is essentially one weak result.
**Blue.** The writeup says "weak, not null" and reports the CI; the extension
does not claim WR works.
**Verdict.** Survives with label. **Residual risk:** Low.
**What would settle it.** A narrower pre-registered WR route-specific signal.

#### T6. TE, OL, and DB are unidentifiable

**Claim.** "TE, OL, and DB are unidentifiable for measurement reasons rather
than evidence of no effect" — `transfer/writeups/01_drill_translation.md:84`.
**Tier.** Measurement.
**Red.** "Unidentifiable" can be read as no effect. The gates fail for different
reasons: TE's outcome reliability is 0.449; OL's signal reliability is 0.448;
DB's outcome reliability is 0.121 and has no usable variance. The headline "the
measurement does not travel" may overstate what is known.
**Blue.** The writeup explicitly distinguishes unidentifiable from null and
defines the gates in the protocol.
**Verdict.** Survives. **Residual risk:** Medium.
**What would settle it.** Better outcome measures for TE/OL/DB.

#### T7. The allocation gap is the strongest transfer

**Claim.** "The allocation gap is the strongest transfer … the performance→role
coefficient is null everywhere" — `transfer/writeups/05_what_transfers.md:34-37`.
**Tier.** Descriptive.
**Red.** The role sample is 233 player-seasons; the strict tails are 4–6
players; most per-quartile CIs cross zero. The gap is a constructed difference
between standardized measures. "Replicates in every position with enough
reliable data" excludes DB and leans on point estimates.
**Blue.** The sign is consistent in WR, OL, and DL; the performance→role null is
consistent; the extension labels the gap descriptive.
**Verdict.** Downgrade: "descriptively consistent, not replicated." **Residual
risk:** High.
**What would settle it.** A larger role sample and per-position CIs.

#### T8. Performance→role is null everywhere

**Claim.** "Current role and draft are positive everywhere; performance is null
everywhere" — `transfer/writeups/03_allocation_gap.md:28`.
**Tier.** Measured null.
**Red.** The CIs are wide: OL +0.190 (−0.057, 0.438); WR −0.018 (−0.232, 0.196).
"Null" cannot rule out a modest positive effect. The performance measures differ
by position.
**Blue.** The point estimates are near zero; current role and draft are positive
everywhere; the extension says "null," not "zero."
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** Equivalence tests.

#### T9. The career ladder is status-legible

**Claim.** "Career start rate rises from 0.03 for late/UDFA players to 0.56 for
early picks; measured performance adds nothing (−0.017, p=0.27) once draft is
controlled" — `transfer/README.md:35-37`.
**Tier.** Descriptive.
**Red.** Career starts are cumulative and mechanically related to role. With
role added, the performance coefficient is −0.033 (CI −0.072, 0.006, p=0.10),
near-significantly negative; the sample collapses from 505 to 392 to 160 across
models. "Status-legible" invites a pricing/causal read the tables do not
support.
**Blue.** The writeup hedges it as descriptive and mechanical, and says it is
weaker evidence than the cap result.
**Verdict.** Downgrade. **Residual risk:** Medium.
**What would settle it.** A non-mechanical career outcome.

### M — Market portfolio

#### M1. Route gating

**Claim.** The portfolio models only the routes the evidence supports —
`implications/markets/PROTOCOL.md:38-48`.
**Tier.** Method.
**Red.** The gate is a judgment. EDGE selection is included despite a
Holm-marginal signal; WR selection is zero; DB and TE get zero role values. A
different gate would produce a different portfolio.
**Blue.** The gate is pre-specified, documented, and applied consistently; the
display-only contract rows are separated; the portfolio says it is not a sum of
every route.
**Verdict.** Survives. **Residual risk:** Low.
**What would settle it.** None; it is a method choice.

#### M2. Position values

**Claim.** IDL $2.45M, EDGE $1.24M, WR $0.40M, OL $0.89M —
`implications/markets/README.md:17-22`.
**Tier.** Inference.
**Red.** These are not bottom-up contract estimates. Selection is a hit-rate
lift × (market value − rookie cost) × picks per year; role is a role-saving
per decision × decisions per cycle × reallocation efficiency. Every input is a
judgment. The EDGE selection uses a Holm-marginal signal; the WR role is
descriptive; the OL role is allocation-only. The values look precise and are
not.
**Blue.** Each row carries its evidence tier; the protocol lists the
calibration parameters; the low and conservative columns show the range.
**Verdict.** Downgrade: call them route scenarios, not market values. **Residual
risk:** High.
**What would settle it.** Bottom-up position valuation from actual contracts.

#### M3. Free agency $6.05M

**Claim.** "Free agency / contract | $6.05M" —
`implications/markets/README.md:23`.
**Tier.** Inference.
**Red.** This is the bottom-up estimate, but it inherits the free-agency
report's uncut annual headline and the 0.40 haircut ambiguity. See F10/F11.
**Blue.** It is the correct replacement for the top-down $24.9M; the dedicated
report is authoritative; the portfolio does not add the legacy components.
**Verdict.** Survives with label: "bottom-up estimate, subject to F10/F11."
**Residual risk:** High.
**What would settle it.** See F10/F11.

#### M4. Portfolio total $11.03M / $5.37M / −$0.68M

**Claim.** "Portfolio total | $11.03M | $5.37M | −$0.68M" —
`implications/markets/README.md:24`.
**Tier.** Inference.
**Red.** The total is an arithmetic sum of routes that share the same role
construct and are not causally additive. The report says the low case is the
conservative guide when role and contract decisions share an organizational
driver (`implications/markets/writeups/05_portfolio.md:38-40`). The low case is
negative. The "conservative" column is not portfolio-wide: every position row's
conservative value equals its base; only the free-agency row drops. The $11.03M
is an independence assumption, not a portfolio.
**Blue.** The portfolio publishes the low case, labels the total an inference,
and says it is not a forecast. The row-level conservative/low columns are
visible.
**Verdict.** Downgrade: "base arithmetic sum under independence; the
overlap-adjusted guide is the low case." **Residual risk:** Critical.
**What would settle it.** A joint adoption model with explicit overlap.

#### M5. EV $4.41M at 40% adoption

**Claim.** "The expected value at the base adoption probabilities is $4.4M" —
`implications/markets/README.md:27-28`.
**Tier.** Inference.
**Red.** EV is 0.40 × the arithmetic total. It inherits the overlap problem and
adds a judgment adoption rate. It is not an expected value in any probabilistic
sense; it is a linear rescale.
**Blue.** The adoption rate is a stated judgment; the low case uses 20%.
**Verdict.** Downgrade. **Residual risk:** High.
**What would settle it.** Adoption data.

#### M6. No double counting

**Claim.** "Position selection + role plus free-agency contract; no double
counting" — `implications/markets/outputs/portfolio.csv` TOTAL note; the
narrative is at `implications/markets/writeups/05_portfolio.md:28-40`.
**Tier.** Accounting.
**Red.** The rule prevents counting the same *row* twice; it does not prevent
counting the same *economic decision* twice. The allocation and contract levers
both price role. The low case concedes this. "No double counting" is an
accounting convention, not an economic result.
**Blue.** The rule is explicit, the legacy contract rows are display-only, and
the low case is the overlap-adjusted guide.
**Verdict.** Survives with label: "no double counting of rows; economic overlap
remains." **Residual risk:** Medium.
**What would settle it.** A joint adoption model.

#### M7. First-mover clock and contract repricing

**Claim.** "The first-mover clock remains 2–5 years. The contract market may
reprice faster than the role market" — `implications/markets/writeups/05_portfolio.md:80`.
**Tier.** Inference.
**Red.** There is no data on adoption timing or repricing speed. The claim is a
plausible story, not an estimate.
**Blue.** It is labeled a clock and a transition rent, not a permanent edge.
**Verdict.** Unresolved. **Residual risk:** Medium.
**What would settle it.** Adoption timing data.

#### M8. Coaching and special teams are descriptive only

**Claim.** "Coaching and special teams last, as descriptive" —
`implications/markets/writeups/05_portfolio.md:78-81`.
**Tier.** Descriptive.
**Red.** The descriptive material could still be overread as a dollar case.
**Blue.** No dollar value is assigned; the section is explicitly descriptive.
**Verdict.** Survives. **Residual risk:** Low.
**What would settle it.** None.

#### M9. The old $24.9M is a 90.6th-percentile team

**Claim.** "The old $24.9M top-down estimate was a 90.6th-percentile synthetic
portfolio" — `implications/markets/README.md:34-37`.
**Tier.** Inference + descriptive.
**Red.** The percentile is computed on the new team distribution, not an
independent validation. The old number and the new distribution are not
independent. The statement is a reconciliation, not a test.
**Blue.** The percentile is a transparent comparison; the bridge shows which
assumptions moved the number; the old number is labeled legacy top-down.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** An independent team distribution.

### F — Free agency

#### F1. 2026 APY role premium +0.179

**Claim.** "The 2026 free-agent APY role premium is +0.179 log points (95% CI
0.022 to 0.336, n=306)" — `implications/free_agency/README.md:28-30`.
**Tier.** Measured association.
**Red.** The lower CI bound is 0.022, close to zero. The estimate is one signing
class; the free-agent sample is selected (only signed players with a prior
performance row); APY is not cash; performance is noisy and role is reliable, so
attenuation can manufacture part of the gap; prior snap share is a proxy for
expected role, not a measure of unearned role. The model cannot distinguish
"teams pay for role" from "teams pay for unmeasured productivity." Adding
contract length and guarantee share as commitment controls reduces the gap to
**+0.049** (−0.093 to 0.191, n=253); years alone gives +0.076, guarantee share
alone +0.150. The premium is not robust to contract-structure controls.
**Blue.** The unconditional association is close to the 2025 cap-ledger gap
(+0.185), the draft-matched gap survives (+0.151), and the repo labels the
estimate a measured association, not causal.
**Verdict.** Downgrade: the unconditional gap is +0.179; the
commitment-controlled gap is +0.049 (CI crosses zero). Report both. **Residual
risk:** High.
**What would settle it.** A forward-role measure (not available for the 2026
class), an errors-in-variables correction, and a pre-registered test of the
contract-structure controls.

#### F2. 2025 cap-ledger +0.185

**Claim.** "the 2025 cap-ledger gap of 0.185 (0.094 to 0.276, n=909)" —
`implications/free_agency/README.md:28-30`.
**Tier.** Measured association.
**Red.** Cap hit is an accounting number, not pay; the performance measure is
role-loaded; the sample excludes OL and specialists and covers 68.7% of
active-cap dollars. The cap gap is the strongest evidence, but it is not APY and
not cash.
**Blue.** n=909, CI excludes zero, and the result is the anchor for the 2026
APY estimate.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** A role-free performance measure.

#### F3. 2025 APY +0.105

**Claim.** "+0.105 (−0.005 to 0.214)" —
`implications/free_agency/README.md:30-31`.
**Tier.** Measured association.
**Red.** The CI crosses zero. The estimate is half the 2026 gap. The difference
may be sample or timing, but the repo's own cross-check does not confirm the
headline.
**Blue.** It is reported as a cross-check, and the repo says the premium is not
stable across every cut.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** A larger sample.

#### F4. 2024 +0.029

**Claim.** "the 2024 sample is +0.029 (−0.169 to 0.227)" —
`implications/free_agency/README.md:30-31`.
**Tier.** Measured association.
**Red.** It is null. The repo calls it a thin sensitivity (n=132), but the
`role_premium.csv` status column marks it "primary" because n≥60. The label is
inconsistent.
**Blue.** The writeup calls it thin; the CI is wide; it is a sensitivity, not a
rejection.
**Verdict.** Survives with label. **Residual risk:** Low.
**What would settle it.** A larger sample.

#### F5. Draft-matched +0.151

**Claim.** "The draft-matched 2026 gap survives at +0.151 (0.016 to 0.286)" —
`implications/free_agency/README.md:32`.
**Tier.** Measured association.
**Red.** Draft capital absorbs 16% of the gap; the CI lower bound is 0.016.
The model still cannot separate role from unmeasured performance.
**Blue.** The gap survives the control; the repo reports the shrinkage.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** A larger sample and an expected-role control.

#### F6. Team-FE +0.099

**Claim.** "Team FE 2025 gap +0.099 (−0.036, 0.234)" —
`implications/free_agency/writeups/00_thesis.md:49`.
**Tier.** Measured association.
**Red.** The CI crosses zero. Team fixed effects absorb half the gap. The
within-team variation may be too small to identify the premium.
**Blue.** It is reported as a sensitivity, not the primary.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** More clusters and years.

#### F7. Team changes earn no premium

**Claim.** "+0.499 (95% CI −0.164 to 1.162)" —
`implications/free_agency/README.md:33-34`.
**Tier.** Measured association.
**Red.** The CI is wide; the interaction is collinear; team-change status is
inferred from the prior-season team, with no signing dates or transaction feed.
The null is not informative about the free-agent premium.
**Blue.** The repo says the free-agent premium is not detectable, and labels the
interaction descriptive.
**Verdict.** Survives with label. **Residual risk:** Low.
**What would settle it.** A transaction feed.

#### F8. Guarantees track role

**Claim.** "a one-unit higher prior-season snap share is associated with 8.3
points higher guarantee share (5.25 to 11.35), and the guarantee share rises
from 0.46 in the bottom snap-share quintile to 0.60 in the top" —
`implications/free_agency/README.md:36-40`.
**Tier.** Measured/descriptive.
**Red.** Guarantee share is bounded and selection-laden; the quintile table is
not in the generated CSVs; the coefficient is for a one-unit change in snap
share, which is a large change; guarantee data may be incomplete. The result is
consistent with role mattering, not proof that role is overpriced.
**Blue.** The guarantee result is consistent with the APY result and is labeled
descriptive. The repo says to net guarantees before claiming cash.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** Guarantee data with signing dates and structure.

#### F9. The premium is concentrated

**Claim.** "the top 10% of contracts account for 51% of the positive premium" —
`implications/free_agency/README.md:39-40`.
**Tier.** Descriptive.
**Red.** Sixteen contracts carry half the premium. The median-team sum is
fragile to a few observations. A single renegotiation can move the headline.
**Blue.** The concentration is reported, and the report says to target the tail.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** A sensitivity that drops the top contracts.

#### F10. The median team carries $7.05M a year

**Claim.** "A median team's 2026 free-agent class carries about $7.0M a year of
modeled role premium" — `README.md:3`; `implications/free_agency/README.md:21`.
**Tier.** Inference.
**Red.** The annual number is **not haircut-adjusted**. In
`implications/free_agency/code/valuation.py:45-46`, the per-contract annual role
premium is `role_premium.clip(lower=0)` with no haircut. `team_table` sums that
uncut value (`:57`). `summary` computes `gross = median_annual ×
(haircut/0.40)` (`:85`), so at the base haircut of 0.40 the gross is the uncut
median. The 0.40 haircut applies only to `contract_total_m` and to the low/high
scaling. If 0.40 is the share of the premium a team can capture, the annual
capturable premium is about **$2.82M gross / $1.82M net**, not $7.05M / $6.05M.
The public headline overstates the capturable annual amount by roughly 3.3×.
**Blue.** The annual role premium is a modeled flow, not a realized saving; the
writeup says the contract-total median ($5.80M) multiplies the APY premium by
years and the 0.40 haircut (`implications/free_agency/writeups/04_valuation.md:21-23`).
The base scenario is the uncut premium by definition, and the low/high cases
scale it. But the scenario label "(all positions, 0.40)" and the public headline
imply the annual number carries the haircut; that is the ambiguity.
**Verdict.** Downgrade: label $7.05M the **uncut** annual role premium, and
report the annual capture at the base haircut separately (~$2.8M gross / ~$1.8M
net). **Residual risk:** Critical.
**What would settle it.** Apply the haircut consistently to the annual flow, or
state explicitly that 0.40 is a contract-total realization parameter only.

#### F11. The net is $6.05M after a $1M cost

**Claim.** "After a **$1M** implementation cost, the modeled difference is
**$6.0M a year**" — `README.md:3`; `implications/free_agency/README.md:22`.
**Tier.** Inference.
**Red.** The $1M is a judgment with no derivation (the protocol ranges it
0.5/1.0/2.0). The net is the uncut gross minus $1M. At the base 0.40 haircut,
the net is about $1.82M, not $6.05M. The headline combines an uncut gross with a
cost, which makes the cost look small relative to the benefit.
**Blue.** The cost is stated; the net is a simple subtraction; the report labels
the dollars inferences. The low case uses a $0.5M cost.
**Verdict.** Downgrade: report the net at the base haircut and source the
implementation cost. **Residual risk:** Critical.
**What would settle it.** A sourced cost estimate and consistent haircut
treatment.

#### F12. Conservative $1.38M / $0.38M

**Claim.** "Conservative: only EDGE/S/CB | $1.38M before cost / $0.38M after" —
`implications/free_agency/README.md:25`.
**Tier.** Inference.
**Red.** The annual figure is also uncut; at the 0.40 haircut it would be
~$0.55M gross / ~−$0.45M net. The EDGE selection evidence is Holm-marginal. The
subset is chosen by a cap-ledger CI, not by an independent free-agency test.
**Blue.** The subset is explicitly CI-supported; the conservative case is
transparent; the low case is near zero.
**Verdict.** Survives with label: "uncut premium for CI-supported positions;
at the base haircut it is near zero or negative." **Residual risk:** Medium.
**What would settle it.** See F10/F15.

#### F13. Low case $0.52M / $0.02M

**Claim.** "Low case | $0.52M before cost / $0.02M after" —
`implications/free_agency/README.md:26`.
**Tier.** Inference.
**Red.** The low case is near zero, which is honest but also shows how fragile
the headline is.
**Blue.** It is reported; the report says the low case is near zero.
**Verdict.** Survives. **Residual risk:** Low.
**What would settle it.** None.

#### F14. Old $24.9M at the 90.6th percentile

**Claim.** "the old top-down $24.9M sits at the 90.6th percentile" —
`implications/free_agency/README.md:42-44`.
**Tier.** Inference.
**Red.** The percentile is computed on the new team distribution; the old and
new numbers are not independent. It is a reconciliation, not a validation.
**Blue.** The bridge shows the drivers; the old number is labeled legacy
top-down.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** An independent team distribution.

#### F15. The 0.40 haircut

**Claim.** "0.40 is a judgment; the low (0.15) and high (0.60) cases show the
range" — `implications/free_agency/writeups/04_valuation.md:73`.
**Tier.** Judgment.
**Red.** The haircut is inherited from the earlier portfolio, not estimated. The
headline is linear in it. The annual/contract-total ambiguity makes it unclear
what the haircut is a haircut *of*. The low/high range is not a confidence
interval.
**Blue.** It is explicitly a judgment, ranged, and the report says so.
**Verdict.** Unresolved. **Residual risk:** High.
**What would settle it.** An elicited or estimated capture rate, or a
negotiation model.

#### F16. The historical file is not a census

**Claim.** "Historical contracts: 30,769 rows, 1983–2022; not a census, no
performance link, age coverage 62%" —
`implications/free_agency/README.md:87-88`.
**Tier.** Descriptive.
**Red.** The row count differs from the protocol's 31,893; the file cannot test
the role premium; the coverage is uneven. The section is context, not evidence.
**Blue.** The writeup says exactly this; the published figure is a coverage
chart, not a trend line.
**Verdict.** Survives. **Residual risk:** Low.
**What would settle it.** None.

#### F17. The public headline: the market pays about $6M a year for role

**Claim.** "The NFL free-agent market pays about $6M a year for role" —
`README.md:1`; `implications/free_agency/README.md:1`.
**Tier.** Inference.
**Red.** The sentence is ambiguous in three ways. "Pays" suggests a market
clearing price, not a conditional association. "About $6M" is the uncut premium
minus a plug cost, not the capturable saving. "For role" can be read as
"players are overpaid for role," "clubs overpay for role," or "role is
underpriced relative to performance." The headline drops the distribution, the
0.40 haircut, the conservative/low cases, and the fact that the top decile
carries half the premium. It is the first thing a reader sees and the least
qualified sentence in the repo.
**Blue.** The README's finding table and the free-agency report carry the
distribution and scenarios; the sentence says "modeled role premium"; the
messaging guide says not to claim players are overpaid.
**Verdict.** Downgrade: "a median team's 2026 free-agent class carries an
uncut modeled role premium of about $7M a year; the capturable annual amount at
the base 0.40 haircut is about $2.8M gross / $1.8M net." **Residual risk:**
Critical.
**What would settle it.** A single reconciled headline with the haircut applied
consistently.

#### F18. Role is snaps, routes, and coverage assignments

**Claim.** "Role is playing time: snaps, routes, coverage assignments" —
`implications/free_agency/README.md:9`.
**Tier.** Definition.
**Red.** The free-agency model uses **snap share only**. Routes and coverage
assignments are not in the model. The definition overstates the measure and
invites the reader to think the model controls for assignment difficulty, which
it does not.
**Blue.** The sentence is a conceptual definition of role, not a variable list.
**Verdict.** Downgrade: "in this model, role is prior-season snap share."
**Residual risk:** Medium.
**What would settle it.** Add routes/coverage to the model or narrow the
definition.

#### F19. Pay tracks role beyond measured performance

**Claim.** "pay that tracks role beyond measured performance" —
`implications/free_agency/README.md:10-11`.
**Tier.** Measured association.
**Red.** "Beyond measured performance" implies the residual is unearned. The
model cannot distinguish unearned role from unmeasured productivity; prior snap
share is a proxy for expected role; attenuation can inflate the role
coefficient. The phrase is an interpretation of a conditional association.
**Blue.** The sentence is followed by "modeled role premium"; the report says it
is not a player ranking of who is overpaid; the messaging guide bans "players
are overpaid."
**Verdict.** Survives with label: "conditional association, not evidence that
role is unearned." **Residual risk:** High.
**What would settle it.** Expected-role and attenuation corrections.

### X — Cross-cutting framing

#### X1. The depth chart does not reward performance

**Claim.** "the depth chart does not reward measured performance" — `README.md:5`.
**Tier.** Framing.
**Red.** The measured claim is "does not detectably reward" with a CI that
includes zero. The public sentence drops "detectably" and states a positive
fact about the depth chart. It is the strongest normative sentence in the repo
and the one most likely to be quoted.
**Blue.** The judged entry says "does not detectably reward" and "absence of
evidence, not proof of zero" (`writeup/submission.md:25`).
**Verdict.** Downgrade: add "detectably." **Residual risk:** High.
**What would settle it.** A wording change.

#### X2. The cap pays performance

**Claim.** "the cap does" — `README.md:5`.
**Tier.** Framing.
**Red.** "Pays" implies intent; the cap number is an accounting residual and the
performance measure is role-loaded. The judged entry says "is associated with."
**Blue.** The judged entry and the caveats use association language; the
headline is a summary.
**Verdict.** Survives with label. **Residual risk:** Medium.
**What would settle it.** Role-free performance measure.

#### X3. The term "role premium"

**Claim.** "role premium" — `README.md:1-3`.
**Tier.** Definition.
**Red.** In labor economics a "premium" usually means extra pay. Here it means
pay attributable to role. The same phrase can be read as "players are overpaid
for role," "clubs overpay for role," or "role is underpriced." The ambiguity is
the whole co-optation problem in one term.
**Blue.** The report defines it as the raw-minus-role coefficient difference and
labels it an association.
**Verdict.** Downgrade: define it once, in plain terms, at first use. **Residual
risk:** High.
**What would settle it.** A definitional edit.

#### X4. Price the role

**Claim.** "Price the role" — `implications/markets/writeups/00_thesis.md:28`;
`implications/free_agency/writeups/07_messaging.md:5-6`.
**Tier.** Normative.
**Red.** This is a recommendation, not a finding. It assumes the model is right
and that clubs should act on it. It is the sentence critics will read as a
pay-cut prescription.
**Blue.** It is labeled a message, not a result.
**Verdict.** Out of scope: normative. **Residual risk:** Medium.
**What would settle it.** None.

#### X5. The allocation gap is structural

**Claim.** "the gap is structural" — `writeup/submission.md:47`.
**Tier.** Inference.
**Red.** "Structural" implies a mechanism that persists beyond the sample. The
evidence is a descriptive decomposition in 233 player-seasons. No identification
strategy supports "structural."
**Blue.** The thesis calls it a structural *reading* and says it is not a moral
claim.
**Verdict.** Downgrade: "descriptively consistent with a structural pattern."
**Residual risk:** High.
**What would settle it.** Identification.

#### X6. Actionable

**Claim.** "actionable" — the brief's criterion, and the repo's claim to meet it
(`writeup/submission.md:42-49`).
**Tier.** Normative.
**Red.** No pilot, no adoption test, no team-level experiment. "Actionable"
means "a plausible action exists," not "the action works."
**Blue.** The repo offers concrete actions and labels them perspectives.
**Verdict.** Downgrade: "plausibly actionable; untested." **Residual risk:**
High.
**What would settle it.** A pilot.

#### X7. The market is inefficient

**Claim.** The work implies the contract market misprices role —
`implications/free_agency/README.md:1`; `implications/writeups/00_thesis.md:37`.
**Tier.** Inference.
**Red.** The model cannot distinguish mispricing from unmeasured productivity,
expected role, or selection. "Inefficient" assumes the model is the correct
price.
**Blue.** The report says "association, not causal"; the messaging guide says
the residual is a deviation from a model, not a verdict.
**Verdict.** Downgrade: "the market prices role in a way this model does not
fully explain." **Residual risk:** High.
**What would settle it.** Expected-role and attenuation corrections.

#### X8. The two levers are additive

**Claim.** The portfolio adds position selection + role + contract —
`implications/markets/README.md:24`.
**Tier.** Inference.
**Red.** The report says the routes are not causally additive and the low case
is the conservative guide; the headline total is a sum. The allocation and
contract levers both price role. If a team plays late picks more, role becomes
more informative and the measured role premium shrinks. The levers are
substitutes, not complements.
**Blue.** The low case is published and is negative; the report says the
arithmetic base and the low case are both reported.
**Verdict.** Concede the additive headline; use the low case. **Residual risk:**
Critical.
**What would settle it.** A joint adoption model.

#### X9. Four headline dollar numbers and claim churn

**Claim.** The repo contains $6.6M gross / $5.6M net (implications), $24.9M
(top-down markets), $7.05M / $6.05M (bottom-up free agency), and $11.03M
(portfolio total) — `implications/README.md:7`;
`implications/markets/README.md:24`; `implications/free_agency/README.md:21-22`.
**Tier.** Clarity.
**Red.** A reader can find four different headline numbers in four READMEs. The
top-down $24.9M is superseded but still appears in the markets README. The
free-agency number is annual and uncut; the implications number is a route sum;
the portfolio is a total. The README headline changed five times in one day
(`6a533be`, `4efb31f`, `04bce03`, `39f5869`, `26fcf25`). Even an honest
correction reads as instability when the history is visible.
**Blue.** Each artifact dates and labels its number; the free-agency report
reconciles the old $24.9M; the markets README says the old number is superseded.
**Verdict.** Concede: publish one reconciled headline table and retire the
others from the front pages. **Residual risk:** Critical.
**What would settle it.** A single source of truth.

#### X10. Post-preregistration exploratory headline

**Claim.** The final headline claims were added after the preregistered tests —
`docs/PREREGISTRATION_v2.md:90-92`; `docs/INTERIOR_BURST_PROTOCOL.md:3`.
**Tier.** Procedural.
**Red.** The preregistered contribution (Yellow/Möbius) returned a wide null.
The role-allocation, Combine-movement, and salary analyses were added after the
data were seen and labeled exploratory. They then became the public headline.
The repo discloses this in the protocols, not in the headline.
**Blue.** The repo is unusually transparent about the sequence; the judged entry
reports the preregistered null; the extensions are labeled exploratory.
**Verdict.** Downgrade: put the genealogy in the headline or a prominent note.
**Residual risk:** High.
**What would settle it.** Pre-register the headline for a future run.

#### X11. Claim genealogy and novelty drift

**Claim.** The entry's contribution was the Yellow/Möbius framework —
`docs/gate_decision.md:45`.
**Tier.** Procedural.
**Red.** The gate decision says public notebooks already cover DL bend, burst,
and pass-rush kinematics, and that the entry's contribution is the Yellow
framework. The Yellow framework failed. The final entry's novelty is a
combination of post-hoc burst and allocation analyses. "Innovation" is the
weakest judging dimension.
**Blue.** The entry's distinct move is the allocation/probe framing, not the
burst metric alone; the gate decision is a planning document, not the final
claim.
**Verdict.** Downgrade: state the novelty as the allocation probe, not the
burst. **Residual risk:** High.
**What would settle it.** None; it is a framing issue.

#### X12. Co-optation and insider threat

**Claim.** The work can be cited by external critics and resisted by insiders
regardless of technical merit — [COOPTATION.md](COOPTATION.md).
**Tier.** Non-empirical.
**Red.** The allocation gap arms a labor critique; the Combine arms a
surveillance critique; the role premium arms a pay-cut critique; the
player-level outputs arm a betting critique; the draft-caste reading arms a
racial-justice critique; the depth-chart null arms a meritocracy critique.
Insiders have identity, institutional, legal, and career reasons to reject the
work.
**Blue.** None. This is not an empirical claim; it is a map of reception.
**Verdict.** Out of scope: non-empirical. **Residual risk:** High.
**What would settle it.** None; monitor citation and reception.

#### X13. Data and artifact inconsistencies

**Claim.** The repo's sample counts and generated artifacts are not internally
consistent.
**Tier.** Data.
**Red.** The 2026 model n is 302 in the protocol, 306 in the output, and 307 in
the README. The strict-tail player count is 12 in the submission and 11 in the
appendix. The historical row count is 30,769 in the writeup and 31,893 in the
protocol. The transfer role panel has DB 69 vs 0 and TE 29 vs 27. The TE Monte
Carlo P50 is $0.48M while the deterministic portfolio reports $0.00M. The 2024
row is labeled "primary" in the CSV and "thin" in the writeup. These are not
fatal, but they are exactly what a hostile reviewer checks first.
**Blue.** Most are rounding, label, or file-version differences; the headline
numbers are stable across the writeups.
**Verdict.** Unresolved: reconcile the counts and regenerate the artifacts.
**Residual risk:** Medium.
**What would settle it.** A single sample audit table and a clean rerun.

## 5. Unresolved register

| ID | Question | What would settle it |
|---|---|---|
| I4 | Is the first-mover window 2–5 years? | Adoption timing data or a club-by-club contract review. |
| M7 | Does the contract market reprice faster than the role market? | The same. |
| F15 | What is the right haircut? | An elicited or estimated capture rate, or a negotiation model. |
| X13 | Which sample counts are authoritative? | A single sample audit and a clean rerun. |
| J4 | Is the burst truly interior-specific? | A pre-specified interaction with adequate power and a clean EDGE placebo. |
| F1 | How much of the role premium is attenuation? | Errors-in-variables correction. |
| F1 | How much is expected role? | A forward-role or contract-length control. |

## 6. Remediation register

These are the original recommendations. A first remediation pass has applied
the dual-dollar presentation, the transfer Holm status, the count fixes, and
the frozen-entry erratum; the applied/remaining status for each finding is in
[scorecard.csv](scorecard.csv). The judged entry is unchanged; its corrections
are in [ERRATUM.md](ERRATUM.md).

| Location | Current | Recommended |
|---|---|---|
| `writeup/submission.md:31` | "about nine parts role to one part performance" | Delete; use "31.7:1 in the full sample, 10.4:1 in the reliable sample" or drop the ratio. |
| `writeup/submission.md:17` | "The Combine signal is position-specific" | "The Combine-movement signal is concentrated in interior linemen; the burst-pressure interaction is not significant." |
| `writeup/submission.md:1` | "The Combine's pressure signal is real" | "The Combine's pressure signal is in-sample and cross-player." |
| `writeup/submission.md:11` | Sacks headline | Add: "the stopwatch is the stronger sack model; the outcome is below the 0.50 reliability gate." |
| `writeup/submission.md:39` | "The wedge is +0.28" | "The cross-construct difference is about 0.28; it is not a behavioral weight." |
| `README.md:3` | "$7.0M a year" | "an uncut modeled role premium of about $7M a year; about $2.8M gross / $1.8M net at the base 0.40 capture assumption." |
| `README.md:5` | "does not reward measured performance" | "does not detectably reward measured performance." |
| `implications/README.md:7` | "$6.6M gross / $5.6M net" | Show the route decomposition; call the total a scenario. |
| `implications/writeups/02_adoption.md:13` | "politically manageable" | Remove; name the losers without the political judgment. |
| `implications/writeups/00_thesis.md:37` | "suppresses" | "is consistent with role persistence." |
| `implications/free_agency/README.md:1` | "pays about $6M a year for role" | "carries a modeled role premium of about $7M a year uncut; about $2.8M at the base capture assumption." |
| `implications/free_agency/README.md:9` | "snaps, routes, coverage assignments" | "prior-season snap share in this model." |
| `implications/free_agency/README.md:21-22` | "$7.05M / $6.05M" | Label the gross "uncut"; report the haircut-adjusted annual capture. |
| `implications/free_agency/writeups/04_valuation.md:12` | "Base (all positions, 0.40)" | Clarify that the annual column is uncut; the 0.40 applies to the contract-total column. |
| `implications/markets/README.md:24` | Portfolio total | Add: "conservative changes only the free-agency row; the low case is the overlap-adjusted guide." |
| `implications/markets/README.md:32-34` | "largest single market" | Add the conservative and overlap caveats inline. |
| `transfer/writeups/01_drill_translation.md:30-33` | "supported" | "borderline after Holm." |
| `transfer/README.md:21-23` | Benchmark first | Put the task-matched signal first; label the benchmark as the positive control. |
| `implications/markets/writeups/05_portfolio.md:66-70` | "lowest-political-cost lever" | Remove; the co-optation annex shows it is not politically costless. |

