# Who to talk to, what to send, and when

**Status:** extension to the 2027 NFL Big Data Bowl entry, not part of it. GitHub only; no Kaggle publication during the competition. Date-stamped 2026-10-19. Staffing and titles must be re-verified before any contact.

## Target roles, not names

Direct email is worth it, but not to GMs. The people whose job is to read this are one or two levels down: football research and analytics, salary-cap and contract analysis, and tracking-product research. A GM receives hundreds of unsolicited decks; an analytics director may open a short note with a reproducible finding.

| Audience | Example titles | Why they care | The ask |
|---|---|---|---|
| Club football research / analytics | Director of Football Research, Senior Data Scientist, Football Analytics Manager | They can test the burst on their own board and their own scheme. | 15 minutes of feedback, or a pointer to the right person. |
| Cap / contract staff | Salary Cap Analyst, Manager of Football Administration, Contract Negotiator | The role-controlled coefficient is a contract argument they can challenge. | Whether the valuation matches their model. |
| Tracking vendors | Product/research lead, football analytics; NGS/Zebra-style providers | The burst-versus-stopwatch result is their product thesis. | Whether the metric is adoptable and how they would validate it. |
| League office | Football operations, management council, CBA analyst | The rookie-scale and role-pipeline question is system-level. | Whether the allocation gap is a policy question. |
| Analytics media | The Athletic, ESPN analytics, PFF, SumerSports | They can cite public work and translate it for a wider audience. | A conversation after the competition deadline. |

Use LinkedIn or public team contact routes. Do not scrape personal email addresses, and do not send to a generic `info@` address and expect a reply. A warm introduction is worth more than ten cold emails.

## The email

Keep it under 150 words, no attachment, three bullets, one ask. The subject line should carry the finding, not the competition.

> **Subject:** 10 Hz Combine burst predicts interior pressure; the stopwatch doesn't
>
> I'm an independent researcher; this is a 2027 Big Data Bowl entry. Three findings:
>
> 1. The 10 Hz burst predicts interior pressure (+0.354 SD/SD, n=64); the 40 and 10-yard split do not (OOS R² −0.113 vs +0.178).
> 2. The cap pays performance (+0.328, +0.143 with role); next-season playing time does not detectably (+0.606 current role, +0.785 draft, −0.011 performance).
> 3. The performance-role gap is mostly role; the strict tail is a 12-player review list.
>
> Writeup: [link]. Repo/notebook: [link].
>
> If this is useful, I'd value 15 minutes of feedback or a pointer to the right person on your research or cap team.

The email leads with the measurement finding, not the structural thesis. The allocation argument is in the writeup; the recipient can draw the conclusion. Leading with "the depth chart is a status market" in a cold email reads as an attack on the coach and closes the door.

## What not to do

- **No mass email.** Five targeted notes beat fifty generic ones. Do not email all 32 clubs.
- **No personal addresses.** Use public team contacts, LinkedIn, or a warm introduction.
- **No causal claims.** Say "association," "descriptive," and "model-reproduced." Do not say the analysis proves coaches are biased.
- **No promised savings.** The dollar figures are inferences; present them as a structured range, not a guarantee.
- **No claim of team endorsement.** A reply is not an endorsement.
- **No raw data.** The competition data is CC BY-NC 4.0 and is not redistributed. Send the writeup and the repo, not the data.
- **No Kaggle publication during the competition.** The judged entry and its attached notebook stay clean. Publish the extension after the deadline if it is still useful.
- **No "Pareto efficient" without naming who loses.** Use "Pareto-adjacent" or "low-political-cost chunk," and state the snap loss.

## Timing

| Wave | When | Audience | Action | Constraint |
|---|---|---|---|---|
| 0 | Now | GitHub | Commit the extension; add the root README pointer. | Judged artifacts frozen; no Kaggle. |
| 1 | T0 + 1 week | Reset teams: Titans, Cardinals, Dolphins | Warm introductions; send the 150-word note. | Verify staffing and titles first. |
| 2 | T0 + 3–4 weeks | Cap-focused teams: Browns, Falcons | Lead with the role-controlled coefficient and the veteran split. | Do not promise cap savings. |
| 3 | T0 + 6–8 weeks | Tracking vendors and league office | Lead with the burst-versus-stopwatch result. | No product endorsement claims. |
| 4 | T0 + 8–12 weeks | Analytics media | Share the public writeup and any club feedback. | After the competition deadline, not before. |

The competition deadline is **2027-01-06 23:59 UTC**. Keep the judged entry and its attached notebook frozen throughout. The extension is a portfolio piece and a conversation starter; it is not a second entry.

## What success looks like

One or two substantive replies, not a front-office offer. A reply that says "we already do this" is useful: it tells you the market is priced and the surplus is smaller. A reply that says "send me the notebook" is a signal to make the code reproducible and the assumptions easy to challenge. A reply that says nothing is the base rate; do not read it as a verdict on the work.

The piece is strong enough that the right reader will remember it. The email's job is to find that reader, not to convince everyone.
