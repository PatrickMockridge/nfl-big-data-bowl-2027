# Messaging: the market pays for performance; price the role

## Message house

**Roof:** the contract market pays for performance; the depth chart pays for
role. Price the role.

**Pillars:**

1. **The APY role premium is measurable, but fragile.** +0.179 log points in the
   2026 class (0.022 to 0.336); +0.185 in the 2025 cap ledger; +0.105 in the
   2025 active APY cross-check; +0.029 in 2024. Adding contract length and
   guarantee share reduces the 2026 gap to +0.049 (−0.093 to 0.191, n=253); the
   premium is not robust to contract-structure controls.
2. **Role is priced in guarantees and length.** A higher snap share predicts a
   higher guarantee share (0.46 → 0.60 across quintiles) and more years.
3. **The dollars are concentrated and the old estimate was upper-tail.** The top
   10% of contracts carry 51% of the positive role premium; the median team is
   $7.05M uncut, the old top-down $24.9M is the 90.6th percentile.

**Foundation:** the tiers. The 2026 APY gap is a measured association; the
guarantee/length links are measured associations; the team and dollar values
are inferences; the team fits are a reading. The message is strongest when the
order is explicit.

## Three lengths

**One sentence.** The free-agent market shows a measurable role premium, but it
is concentrated in a small high-APY tail; a median team's actual renewal wave
carries about $7M uncut, or about $1.8M net at the 0.40 capture assumption, not
the $25M the synthetic portfolio implied.

**Three sentences.** The 2026 free-agent APY role premium is +0.179 log points
(0.022 to 0.336), close to the 2025 cap-ledger gap of 0.185, but it falls to
+0.049 when contract length and guarantee share are added as commitment
controls. Role also predicts guarantees and contract length, so the correction
is not only headline APY. The premium is concentrated: the top 10% of contracts
carry 51% of it, and the old $24.9M is a 90th-percentile team; the median team
is about $7.05M uncut / $1.82M capture net.

**One paragraph.** The market portfolio's free-agency number was top-down: a
coefficient difference multiplied by a synthetic portfolio. The player-level
investigation uses the actual 2026 signing class. The APY role premium is +0.179
(0.022 to 0.336, n=306), close to the cap-ledger 0.185; the 2025 cross-check is
0.105 and the 2024 sample is null. Role predicts guarantees and length. The
premium is concentrated: 16 contracts carry half of it, and the median team is
$7.05M uncut / $1.82M capture net. The old $24.9M is the 90.6th percentile; the
conservative EDGE/S/CB subset is $1.38M uncut / −$0.45M capture net. The honest
message is: price the role, target the tail, and do not sell a median team the
top-decile number.

## Audience framings

| Audience | Lead with | Do not lead with | The ask |
|---|---|---|---|
| GM / roster | The role premium and the concentrated tail; median team ~$7M uncut / ~$1.8M capture net. | The old $24.9M as the typical case. | Price the next renewal wave on role-controlled performance. |
| Cap manager | APY, guarantees, and length together; role predicts guarantees. | APY alone, or a promise of cash savings. | Model the team's own renewal ledger; target the top decile. |
| Analytics | The 2026 APY gap, the 2025 cross-check, the 2024 null, the draft-matched 0.151. | A single coefficient without the sample and robustness. | Re-run the model in the team's own data. |
| Agent / player | The market pays performance; role is part of the price. The model is symmetric; an agent can use the same coefficient to argue role is underpriced. | "Players are overpaid"; the model is not a verdict. | Negotiate on role and guarantees, not only APY. |
| League office | The contract-market role premium; the concentration. | Club-specific blame. | Ask whether the renewal market prices role consistently. |
| Media / portfolio | The measured association, the distribution, the upper-tail correction. | A single big number. | Keep the measured/descriptive/inferred separation explicit. |

## Proof points

| Number | Status | Source |
|---|---|---|
| 2026 FA APY gap +0.179 (0.022, 0.336) | measured association | `outputs/role_premium.csv` |
| 2025 cap-ledger gap +0.185 (0.094, 0.276) | measured association | `outputs/role_premium.csv` |
| 2025 APY gap +0.105 (−0.005, 0.214) | measured association | `outputs/role_premium.csv` |
| 2024 APY gap +0.029 (−0.169, 0.227) | measured association, thin | `outputs/role_premium.csv` |
| Draft-matched gap +0.151 (0.016, 0.286) | measured association | `outputs/role_premium.csv` |
| Guarantee share: snap-share coefficient 8.30 | measured association | `outputs/guarantee_years_models.csv` |
| Top 10% of contracts = 51.1% of positive role premium | descriptive | `outputs/surplus_concentration.csv` |
| Median team annual role premium $7.05M | inference | `outputs/valuation_summary.csv` |
| Old $24.9M = 90.6th percentile | inference + descriptive | `outputs/valuation_bridge.csv` |
| Portfolio total $11.03M base / $5.37M conservative | inference | `implications/markets/outputs/portfolio.csv` |

## Objection handling

| Objection | Response |
|---|---|
| "The old report said $24.9M." | That was a synthetic upper-tail team. The actual median team's 2026 class is $7.05M uncut / $1.82M capture net; the old number is the 90.6th percentile. |
| "The 2025 cross-check is only 0.105." | Correct. The 2026 event sample is the appropriate pre-signing sample and is larger; the 2025 active-contract sample is a cross-check, not the primary. |
| "The 2024 sample is null." | It is thin (n=132) and uses concurrent performance; it is a sensitivity, not a rejection. |
| "Draft capital absorbs the gap." | It absorbs part: 0.179 → 0.151 in the draft-matched sample. The gap survives, but smaller. |
| "Guarantees mean the saving is not real." | Role predicts guarantees; the report says the APY saving is not the same as a cash saving. Net the guarantee before claiming cash. |
| "Is this causal?" | No. Free agents are selected; the estimates are conditional associations. The report labels every dollar as an inference. |

## What not to say

1. Not "the free-agent market proves $25M per team." The median team is ~$6M
   net; the old number is an upper-tail synthetic portfolio.
2. Not "players are overpaid." The residual is a deviation from a model, not a
   verdict.
3. Not "the role premium is stable." The 2025 cross-check is marginal and the
   2024 sample is null.
4. Not "APY is the whole saving." Role predicts guarantees and years; net them.
5. Not "free agents earn a premium." The team-change coefficient is not
   distinguishable from zero after controls.
6. Not "the historical file shows positional repricing." It is not a census.
7. Not a single dollar figure without the distribution and the low/conservative
   cases.
