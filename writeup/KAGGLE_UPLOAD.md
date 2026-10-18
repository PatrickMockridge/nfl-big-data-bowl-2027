# Kaggle writeup upload — step by step

The writeup page must be created in the Kaggle UI; the Kaggle CLI has no
command for creating competition writeups. Everything is prepared so the
upload is copy-paste.

## 1. Create the writeup

Open:

https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/writeups

Click **Create Writeup** / **New Writeup**.

Suggested title (49 characters):

**The testing is informative; the decisions are not**

Alternate (52 characters):

**The Allocation Gap: Combine Signal, Depth Chart, Cap**

## 2. Paste the body

Open `writeup/kaggle_writeup.md` and paste the whole file into the Kaggle
writeup editor. It is the same 1,993-word writeup as `writeup/submission.md`,
but the six image paths point at public raw GitHub URLs:

- `combine_linkage.png`
- `salary_efficiency.png`
- `qb_premium.png`
- `next_role_forest.png`
- `persistence_within_player.png`
- `overpay_quartiles.png`

If the writeup page already exists, replace the body with this version and
republish; the chart redesign changed the figure numbers and captions.

If Kaggle renders the external images, publish directly.

If the images do not render, upload the six PNGs from `writeup/figures/`
through the editor's image button and replace each raw GitHub URL with the
uploaded image. The captions already name the figures.

## 3. Attach the public notebook

In the writeup's notebook/link field, attach or link:

https://www.kaggle.com/code/patrickm/nfl-bdb-2027-the-allocation-gap

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

- Words: 1,993 (limit: 2,000)
- Figures: 6
- Tables: 2
- Total visuals: 8 (limit: fewer than 10)
- Public notebook: yes
- Combine sensor tracking → regular-season performance linkage: explicit in
  Part 1 "What we found" and Part 2 "Combine linkages"

## Repo

https://github.com/PatrickMockridge/nfl-big-data-bowl-2027
