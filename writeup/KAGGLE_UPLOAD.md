# Kaggle writeup upload — step by step

**Status (2026-10-20): revised writeup, host-confirmed salary data.** This
supersedes the original judged text frozen at `c652424`; the original remains
in git history. The revision adds the salary tier (Tier 2) and applies the
audit wording corrections. The measured core is unchanged.

The writeup page must be created in the Kaggle UI; the Kaggle CLI has no
command for creating competition writeups. Everything is prepared so the
upload is copy-paste.

## 1. Create the writeup

Open:

https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/writeups

Click **Create Writeup** / **New Writeup**.

Suggested title (67 characters):

**The Combine burst predicts pressure; the allocation gap has a price**

Alternate (56 characters):

**The Combine burst predicts pressure; the gap has a price**

## 2. Paste the body

Open `writeup/kaggle_writeup.md` and paste the whole file into the Kaggle
writeup editor. It is the same 1,814-word writeup as `writeup/submission.md`,
but the five image paths point at public raw GitHub URLs:

- `measurement_panel.png`
- `pricing_allocation_panel.png`
- `gap_agent_panel.png`
- `fa_headline.png`
- `fa_role_premium.png`

The URLs currently point at `main`; pin them to the revision commit for
immutable images. If the writeup page already exists, replace the body with
this version and republish; the revision adds Tier 2 (the
contract market) and the dual-dollar figures.

If Kaggle renders the external images, publish directly.

If the images do not render, upload the five PNGs from `writeup/figures/`
(the three composites) and `implications/free_agency/writeups/figures/`
(`fa_headline.png`, `fa_role_premium.png`) through the editor's image button
and replace each raw GitHub URL with the uploaded image. The captions already
name the figures.

The salary analysis is included under the host's confirmation: "Using external
data on player salaries is appropriate for a submission as long as it is
publicly available and free" (Tom Bliss, discussion 751037).

## 3. Attach the public notebook

In the writeup's notebook/link field, attach or link the public notebook:

https://www.kaggle.com/code/patrickm/nfl-bdb-2027-combine-allocation-price

The earlier notebook remains at
`https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap` as the
record. Publish `notebooks/03_final_public_v2.ipynb` under the
`nfl-bdb-2027-combine-allocation-price` slug; if the slug is taken, use the
published URL and update the writeup.

This satisfies the competition's "attached Public Kaggle Notebook" pass/fail
requirement.

## 4. Publish and copy the URL

Publish the writeup. The URL will look like:

`https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/writeups/<slug>`

Copy that URL.

## 5. Submit

Open the competition submission form and paste the writeup URL into the
**Writeup URL** field. If the form instead asks for a notebook URL, use:

`https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap`

but the competition's pass/fail language indicates the writeup page is the
container and the notebook is attached to it.

## Limits check

- Words: 1,814 (limit: 2,000)
- Figures: 5 (three composites + `fa_headline` + `fa_role_premium`)
- Tables: 4 (dollar scenarios, football scorecard, selected models, robustness)
- Total visuals: 9 (limit: fewer than 10)
- Public notebook: yes
- Combine sensor tracking → regular-season performance linkage: explicit in
  Part 1 Tier 0 and Part 2 "Models"
- External salary data: public and free; host confirmed (discussion 751037)
- Revision: the original judged text is at `c652424`; this is the
  revised writeup with host-confirmed salary data

## Repo

https://github.com/PatrickMockridge/nfl-big-data-bowl-2027
