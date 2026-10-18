"""Build the self-contained public Kaggle notebook (robust core)."""

from __future__ import annotations

import base64
import zlib
from pathlib import Path

import nbformat as nbf
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "02_final_public.ipynb"
SAL = ROOT / "outputs" / "salary"

import sys

sys.path.insert(0, str(ROOT / "src"))
from viz.figures import LABELS  # noqa: E402

# Embed the derived salary panel, rent table, and soccer table so the notebook
# is self-contained on Kaggle without an external dataset attachment. The
# derivation and source notes are in the repository (src/salary/,
# docs/EXTERNAL_DATA.md, docs/SOCCER_DATA.md).
SALARY_COLS = [
    "season", "team", "star_share", "rookie_snap_share", "homegrown_snap_share",
    "youth_snap_share", "qb_share", "cap_qb_share", "cap_star_share", "wins",
    "point_diff", "off_epa_per_play", "wins_per_100m", "point_diff_per_100m",
    "off_epa_per_100m", "log_payroll", "season_c",
]
_salary_csv = pd.read_csv(SAL / "team_salary_panel.csv")[SALARY_COLS].to_csv(index=False)
_rent_csv = pd.read_csv(SAL / "rent_quartiles.csv").to_csv(index=False)
_soccer_csv = pd.read_csv(SAL / "soccer_table.csv").to_csv(index=False)
_weekly_csv = pd.read_csv(ROOT / "outputs" / "discovery" / "weekly_role.csv").to_csv(index=False)
SALARY_B64 = base64.b64encode(zlib.compress(_salary_csv.encode())).decode()
RENT_B64 = base64.b64encode(zlib.compress(_rent_csv.encode())).decode()
SOCCER_B64 = base64.b64encode(zlib.compress(_soccer_csv.encode())).decode()
WEEKLY_B64 = base64.b64encode(zlib.compress(_weekly_csv.encode())).decode()

md_intro = """# The testing is informative; the decisions are not

**NFL Big Data Bowl 2027 — public analysis notebook**

**What is new**

- The 10 Hz Combine signal predicts performance (**+0.299 SD/SD** in the full pipeline) but not playing time (**−0.019**). This notebook's self-contained reconstruction gives **+0.41** and **−0.05**; the pattern and the playing-time null are the same. Small differences come from rebuilding the movement composite and performance residuals from the raw files.
- Next-season playing time follows current playing time (**+0.606**) and draft position (**+0.785**), not performance (**−0.011**); the within-player change is **−0.095** (p = 0.11).
- The weekly check: next-week playing time follows this-week playing time (**+0.753**); this-week performance does not (**−0.006**, p = 0.59).
- The cap repeats the pattern: star share **−0.70** (p = 0.89); rookie snap share **−28.4** (p = 0.004); homegrown **+9.2** (p = 0.001); QB spending flattens at about **14% of payroll**.
- The measurement is working; the decisions are not.

This notebook reproduces the core results from the raw competition data plus a self-contained salary panel and a week-to-week check derived from public OverTheCap and nflverse data. It uses the 10 Hz Combine tracking and the tracking-derived Next Gen Stats in `player_play`. Competition data is CC BY-NC 4.0; do not redistribute.
"""

code_setup = r'''
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score

KAGGLE = Path("/kaggle/input/nfl-big-data-bowl-2027")
LOCAL = Path("data/raw")
if KAGGLE.exists():
    DATA = KAGGLE
elif LOCAL.exists():
    DATA = LOCAL
else:
    import kagglehub
    root = Path(kagglehub.competition_download("nfl-big-data-bowl-2027"))
    DATA = next(root.rglob("players.csv")).parent
print("Data:", DATA)

players = pd.read_csv(DATA / "players.csv")
combine = pd.read_csv(DATA / "combine_results.csv")
games = pd.read_csv(DATA / "games.csv")
career = pd.read_csv(DATA / "player_career_successes.csv")
games["home_team_abbr"] = games["home_team_abbr"].replace({"LA": "LAR"})
games["visitor_team_abbr"] = games["visitor_team_abbr"].replace({"LA": "LAR"})
header = pd.read_csv(DATA / "player_play.csv", nrows=0).columns
usecols = [c for c in [
    "game_id","play_id","team_abbr","nfl_id","lined_up_position","possession_team",
    "player_get_off","pressure_allowed","pass_result","separation_at_pass_forward",
    "route_ran","target","cushion","down","yards_to_go","pass_length",
    "in_motion_at_ball_snap","blitzing","pass_rushers_encountered","dropback_duration",
    "coverage_assignment","receiver_alignment","team_coverage_man_zone",
    "team_coverage_type","yardline_number","expected_points",
] if c in header]
pp = pd.read_csv(DATA / "player_play.csv", usecols=usecols)
pp = pp.merge(games[["game_id","season","week","season_type"]], on="game_id", how="left")
pp = pp[(pp["season_type"] == "REG") & pp["nfl_id"].isin(players["nfl_id"])].copy()
pp["team_abbr"] = pp["team_abbr"].replace({"LA": "LAR"})
pp["nfl_position"] = pp["nfl_id"].map(players.set_index("nfl_id")["nfl_position"])
group_map = {"WR":"WR","TE":"TE","CB":"DB","SS":"DB","FS":"DB","DB":"DB",
             "T":"OL","G":"OL","C":"OL","DE":"DL","DT":"DL","NT":"DL","OLB":"DL",
             "ILB":"LB","MLB":"LB"}
pp["position_group"] = pp["nfl_position"].map(group_map).fillna("OTHER")
print(pp.shape)
'''

code_perf = r'''
GROUPS = {"DL":{"DE","DT","NT","OLB"},"WR":{"WR"},"TE":{"TE"},"OL":{"T","G","C"},
          "DB":{"CB","SS","FS","DB"},"LB":{"ILB","MLB"}}
NUM = ["yards_to_go","pass_length","cushion","dropback_duration","pass_rushers_encountered",
       "yardline_number","expected_points"]
CAT = ["route_ran","team_coverage_man_zone","team_coverage_type","down",
       "in_motion_at_ball_snap","blitzing","coverage_assignment","receiver_alignment","season"]

def outcome(group, df):
    if group == "DL": return -df["player_get_off"].astype(float)
    if group in {"WR","TE"}: return df["separation_at_pass_forward"]
    if group == "OL": return -df["pressure_allowed"].astype(float)
    if group == "DB": return -df["pass_result"].map({"C":1.0,"I":0.0,"IN":0.0})
    return -df["player_get_off"].astype(float)

def model():
    num = Pipeline([("imp",SimpleImputer(strategy="median",add_indicator=True)),("sc",StandardScaler())])
    cat = Pipeline([("imp",SimpleImputer(strategy="most_frequent")),
                    ("oh",OneHotEncoder(handle_unknown="ignore",sparse_output=True))])
    pre = ColumnTransformer([("num",num,NUM),("cat",cat,CAT)],sparse_threshold=1.0)
    return Pipeline([("pre",pre),("ridge",Ridge(alpha=1.0))])

def residuals(group):
    d = pp[pp["nfl_id"].isin(players.loc[players["nfl_position"].isin(GROUPS[group]),"nfl_id"])].copy()
    d["y"] = outcome(group, d)
    d = d.dropna(subset=["y"])
    if len(d) < 50: return pd.DataFrame()
    X, y, g = d[NUM+CAT], d["y"].to_numpy(), d["nfl_id"].to_numpy()
    r = np.full(len(d), np.nan)
    for tr, te in GroupKFold(5).split(X, y, g):
        m = model().fit(X.iloc[tr], y[tr])
        r[te] = y[te] - m.predict(X.iloc[te])
    d["residual"] = r
    season = d.groupby(["nfl_id","season"])["residual"].agg(raw_mean="mean",n_plays="count",within_var="var").reset_index()
    season["within_var"] = season["within_var"].fillna(0)
    noise = season["within_var"] / season["n_plays"]
    tau2 = max(float(season["raw_mean"].var(ddof=0) - noise.mean()), 0.0)
    season["shrunk_mean"] = season["raw_mean"]*tau2/(tau2+noise) if tau2 > 0 else 0.0
    season["group"] = group
    return season

perf_list = []
for g in GROUPS:
    s = residuals(g)
    if len(s):
        perf_list.append(s)
perf = pd.concat(perf_list, ignore_index=True)
perf = perf.rename(columns={"raw_mean":"perf_raw","n_plays":"perf_n","within_var":"perf_var","shrunk_mean":"perf_shrunk"})
print(perf.groupby("group").size())
'''

code_panel = r'''
pp["is_defense"] = pp["team_abbr"] != pp["possession_team"]
team = pp.groupby(["nfl_id","season","team_abbr"]).size().reset_index(name="team_snaps")
n_teams = team.groupby(["nfl_id","season"])["team_abbr"].nunique().rename("n_teams").reset_index()
primary = (team.sort_values("team_snaps").drop_duplicates(["nfl_id","season"],keep="last")
           [["nfl_id","season","team_abbr"]].rename(columns={"team_abbr":"primary_team"}))
ps = pp.groupby(["nfl_id","season"]).agg(
    snaps=("game_id","size"), games=("game_id","nunique"),
    pass_rush_plays=("player_get_off",lambda x:x.notna().sum()),
    pass_block_plays=("pressure_allowed",lambda x:x.notna().sum()),
    coverage_plays=("coverage_assignment",lambda x:x.notna().sum()),
    routes=("route_ran",lambda x:x.notna().sum())).reset_index()
ps = ps.merge(primary, on=["nfl_id","season"]).merge(n_teams, on=["nfl_id","season"])
ps["position_group"] = ps["nfl_id"].map(pp.drop_duplicates("nfl_id").set_index("nfl_id")["position_group"])
ps = ps.merge(perf[["nfl_id","season","perf_shrunk","perf_n"]], on=["nfl_id","season"], how="left")
ps["role_pg"] = ps["snaps"] / ps["games"].replace(0,np.nan)
ps["role_pass"] = ps[["pass_rush_plays","routes","pass_block_plays","coverage_plays"]].max(axis=1) / ps["games"].replace(0,np.nan)
room = ps.groupby(["season","primary_team","position_group"])["snaps"].transform("sum")
ps["role_share"] = ps["snaps"] / room.replace(0,np.nan)
for col, name in [("role_pg","role_z"),("role_pass","role_pass_z"),("role_share","role_share_z")]:
    ps[name] = ps.groupby(["position_group","season"])[col].transform(
        lambda x:(x-x.mean())/x.std(ddof=0) if x.std(ddof=0)>0 else x*0)
ps["perf_z"] = ps.groupby(["position_group","season"])["perf_shrunk"].transform(
    lambda x:(x-x.mean())/x.std(ddof=0) if x.std(ddof=0)>0 else x*0)
ps = ps.sort_values(["nfl_id","season"])
ps["next_role"] = ps.groupby("nfl_id")["role_z"].shift(-1)
ps["next2_role"] = ps.groupby("nfl_id")["role_z"].shift(-2)
ps["next_season"] = ps.groupby("nfl_id")["season"].shift(-1)
ps["next2_season"] = ps.groupby("nfl_id")["season"].shift(-2)
ps = ps.merge(players[["nfl_id","display_name","draft_year","draft_overall_pick"]], on="nfl_id", how="left")
ps = ps.merge(combine[["nfl_id","ngs_final_score","ngs_college_production_score","ngs_athleticism_score"]], on="nfl_id", how="left")
# Draft-capital percentile on unique players, not player-seasons.
pu = players.merge(combine[["nfl_id","ngs_final_score","ngs_college_production_score","ngs_athleticism_score"]], on="nfl_id", how="left")
pu["position_group"] = pu["nfl_position"].map(group_map).fillna("OTHER")
pu["B_draft"] = 0.0
for (yr, pos), idx in pu.groupby(["draft_year","position_group"]).groups.items():
    sub = pu.loc[idx]; picks = sub["draft_overall_pick"]; r = picks.rank(method="average", ascending=False)
    pu.loc[idx,"B_draft"] = (r-1)/max(len(sub)-1,1)
    pu.loc[sub.index[picks.isna()],"B_draft"] = 0.0
pu["B_draft"] = pu["B_draft"].clip(0,1)
ps = ps.merge(pu[["nfl_id","B_draft"]], on="nfl_id", how="left")
for col in ["ngs_final_score","ngs_college_production_score"]:
    ps[col+"_z"] = (ps[col]-ps[col].mean())/ps[col].std(ddof=0)
ps["prestige_nodraft"] = ps[["ngs_final_score_z","ngs_college_production_score_z"]].mean(axis=1)
ps = ps.merge(career[["nfl_id","career_offensive_snaps","career_defensive_snaps",
                      "career_special_teams_snaps","career_games_active","career_games_started"]], on="nfl_id", how="left")
ps["career_snaps"] = ps[["career_offensive_snaps","career_defensive_snaps","career_special_teams_snaps"]].sum(axis=1)
ps["season_c"] = ps["season"].astype(str)
print(ps.shape)
'''

code_models = r'''
t1 = ps[(ps["next_season"] == ps["season"]+1) & ps["next_role"].notna()].copy()
t2 = ps[(ps["next2_season"] == ps["season"]+2) & ps["next2_role"].notna()].copy()
fe = " + C(position_group) + C(season_c)"
base = t1[t1["position_group"] != "DB"].dropna(
    subset=["role_z","perf_z","B_draft","prestige_nodraft","season_c","position_group","primary_team"]).copy()
t2 = t2[t2["position_group"] != "DB"].dropna(
    subset=["role_z","perf_z","B_draft","season_c","position_group"]).copy()

def fit(formula, data):
    return smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups":data["nfl_id"]})

concurrent = fit(f"role_z ~ perf_z + B_draft + prestige_nodraft{fe}", base)
base["role_gap"] = concurrent.resid
next1 = fit(f"next_role ~ role_z + perf_z + B_draft{fe}", base)
next1p = fit(f"next_role ~ perf_z + B_draft + prestige_nodraft{fe}", base)
next2 = fit(f"next2_role ~ role_z + perf_z + B_draft{fe}", t2)
base["team_role_mean"] = base.groupby(["primary_team","season"])["role_z"].transform("mean")
base = base.dropna(subset=["team_role_mean"]).copy()
next1_team = fit(f"next_role ~ role_z + perf_z + B_draft + team_role_mean{fe}", base)
sens = {}
for role_col, label in [("role_pass_z","pass-play role"),("role_share_z","cohort role share")]:
    sub = t1[t1["position_group"] != "DB"].dropna(
        subset=[role_col,"perf_z","B_draft","next_role","season_c","position_group"]
    )
    sens[label] = fit(f"next_role ~ {role_col} + perf_z + B_draft{fe}", sub)
dd = ps[ps["position_group"] != "DB"].sort_values(["nfl_id","season"]).copy()
dd["d_role"] = dd.groupby("nfl_id")["role_z"].diff()
dd["d_perf"] = dd.groupby("nfl_id")["perf_z"].diff()
dd["d_next"] = dd.groupby("nfl_id")["season"].diff()
diff = dd[dd["d_next"] == 1].dropna(subset=["d_role","d_perf"])
diff_fit = fit("d_role ~ d_perf", diff)

def show(fit, label, terms):
    print(label)
    for term in terms:
        if term not in fit.params: continue
        ci = fit.conf_int().loc[term]
        print(f"  {term}: {fit.params[term]:+.3f} ({ci[0]:+.3f}, {ci[1]:+.3f}) p={fit.pvalues[term]:.3g}")

show(concurrent, "Concurrent role", ["perf_z","B_draft","prestige_nodraft"])
show(next1, "Next role", ["role_z","perf_z","B_draft"])
show(next1p, "Next role (performance only)", ["perf_z","B_draft","prestige_nodraft"])
show(next2, "Role at t+2", ["role_z","perf_z","B_draft"])
show(next1_team, "Next role (team control)", ["role_z","perf_z","B_draft","team_role_mean"])
show(diff_fit, "Within-player change", ["d_perf"])

# Position replication and role-measure sensitivity tables for figures.
pos_rows = []
for g, sub in t1.groupby("position_group"):
    if len(sub) < 25:
        continue
    if g == "DB":
        sub = sub.dropna(subset=["role_z","B_draft","next_role"])
        f = fit("next_role ~ role_z + B_draft", sub)
        pos_rows.append({"position":g,"n":len(sub),
                         "role":f.params["role_z"],"role_lo":f.conf_int().loc["role_z",0],"role_hi":f.conf_int().loc["role_z",1],
                         "perf":np.nan,"perf_lo":np.nan,"perf_hi":np.nan,
                         "draft":f.params["B_draft"],"draft_lo":f.conf_int().loc["B_draft",0],"draft_hi":f.conf_int().loc["B_draft",1]})
    else:
        sub = sub.dropna(subset=["role_z","perf_z","B_draft","next_role"])
        f = fit("next_role ~ role_z + perf_z + B_draft", sub)
        pos_rows.append({"position":g,"n":len(sub),
                         "role":f.params["role_z"],"role_lo":f.conf_int().loc["role_z",0],"role_hi":f.conf_int().loc["role_z",1],
                         "perf":f.params["perf_z"],"perf_lo":f.conf_int().loc["perf_z",0],"perf_hi":f.conf_int().loc["perf_z",1],
                         "draft":f.params["B_draft"],"draft_lo":f.conf_int().loc["B_draft",0],"draft_hi":f.conf_int().loc["B_draft",1]})
pos_df = pd.DataFrame(pos_rows)
sens_rows = []
for label, fit_obj, role_term in [
    ("Raw snaps", next1, "role_z"),
    ("Pass-play role", sens["pass-play role"], "role_pass_z"),
    ("Cohort role share", sens["cohort role share"], "role_share_z"),
    ("Team control", next1_team, "role_z"),
]:
    for key, term in [("role", role_term), ("performance", "perf_z"), ("draft", "B_draft")]:
        if term not in fit_obj.params:
            continue
        ci = fit_obj.conf_int().loc[term]
        sens_rows.append({"model": label, "series": key, "coef": fit_obj.params[term],
                          "lo": ci[0], "hi": ci[1]})
sens_df = pd.DataFrame(sens_rows)

# OOF role prediction.
X = base[["role_z","perf_z","B_draft","position_group","season_c"]]
y = base["next_role"]; groups = base["nfl_id"].to_numpy()
oof = np.full(len(base), np.nan); oof_perf = []
for tr, te in GroupKFold(5).split(X, y, groups):
    f = smf.ols("next_role ~ role_z + perf_z + B_draft + C(position_group) + C(season_c)",
                data=base.iloc[tr]).fit()
    oof[te] = f.predict(base.iloc[te]); oof_perf.append(float(f.params["perf_z"]))
print("OOF R2", round(r2_score(y, oof),3), "perf coef range", round(min(oof_perf),3), round(max(oof_perf),3))

# Descriptive tails on reliable samples.
tail = base[base["perf_n"] >= 50].copy()
tail["allocation"] = "mid"
tail.loc[(tail["perf_z"] >= tail["perf_z"].quantile(.75)) & (tail["role_gap"] <= tail["role_gap"].quantile(.25)),
         "allocation"] = "low role / high performance"
tail.loc[(tail["perf_z"] <= tail["perf_z"].quantile(.25)) & (tail["role_gap"] >= tail["role_gap"].quantile(.75)),
         "allocation"] = "high role / low performance"
print(tail.groupby("allocation")[["role_z","perf_z","role_gap","next_role"]].agg(["count","mean"]).round(3))
'''

code_combine = r'''
# Generic 10 Hz Combine movement composite and its linkage.
ct = pd.read_csv(DATA/"combine_tracking.csv", usecols=["event_id","nfl_id","entity_type","time","x","y","s","a","drill_name","attempt"])
ct = ct[(ct.entity_type=="PLAYER") & ct.nfl_id.notna()].copy()
ct["time"] = pd.to_datetime(ct["time"])
ct = ct.sort_values(["event_id","nfl_id","attempt","time"])
g = ct.groupby(["event_id","nfl_id","attempt"])
ct["elapsed"] = (ct["time"]-g["time"].transform("first")).dt.total_seconds()
ct["from_start"] = np.hypot(ct["x"]-g["x"].transform("first"), ct["y"]-g["y"].transform("first"))
def attempt_stats(d):
    d=d.sort_values("time"); e=d["elapsed"].to_numpy(); s=d["s"].to_numpy(); a=d["a"].to_numpy()
    x=d["x"].to_numpy(); y=d["y"].to_numpy(); dist=np.hypot(x-x[0],y-y[0]); path=np.sum(np.hypot(np.diff(x),np.diff(y)))
    hit=np.where(dist>=1)[0]; first=e<=0.5
    return pd.Series({"max_speed":s.max(),"max_accel_first":a[first].max() if first.any() else np.nan,
                      "time_to_1yd":e[hit[0]] if len(hit) else np.nan,
                      "path_eff":min(dist[-1]/path,1.0) if path>0 else np.nan})
att = g.apply(attempt_stats, include_groups=False).reset_index()
att = att.merge(ct[["event_id","nfl_id","attempt","drill_name"]].drop_duplicates(), on=["event_id","nfl_id","attempt"], how="left")
att["position_group"] = att["nfl_id"].map(
    players.drop_duplicates("nfl_id").set_index("nfl_id")["nfl_position"]
).map(group_map).fillna("OTHER")
for col in ["max_speed","max_accel_first","time_to_1yd","path_eff"]:
    att[col]=att.groupby(["drill_name","position_group"])[col].transform(
        lambda x:(x-x.mean())/x.std(ddof=1) if x.std(ddof=1)>0 else x*0)
cm = att.groupby("nfl_id").agg(speed=("max_speed","mean"),accel=("max_accel_first","mean"),
                               time1=("time_to_1yd","mean"),path=("path_eff","mean")).reset_index()
parts = cm[["speed","accel","path"]].copy()
parts["time1"] = -cm["time1"]
parts = parts.apply(lambda x:(x-x.mean())/x.std(ddof=0))
cm["combine_movement"] = parts.mean(axis=1)
print("Combine movement players:", len(cm))

perf_sample = ps.merge(cm, on="nfl_id", how="left").dropna(subset=["combine_movement","perf_z"])
perf_sample = perf_sample[perf_sample["position_group"] != "DB"].copy()
role_sample = base[(base["perf_n"] >= 50) & base["role_gap"].notna()].merge(
    cm, on="nfl_id", how="left").dropna(subset=["combine_movement"])
combine_rows = []
for data, formula, label in [
    (perf_sample,"perf_z ~ combine_movement + B_draft + C(position_group) + C(season_c)","performance"),
    (role_sample,"role_z ~ combine_movement + B_draft + C(position_group) + C(season_c)","role"),
    (role_sample,"role_gap ~ combine_movement + role_z + B_draft + C(position_group)","role gap"),
]:
    f=smf.ols(formula,data=data).fit(cov_type="cluster",cov_kwds={"groups":data["nfl_id"]})
    ci=f.conf_int().loc["combine_movement"]
    combine_rows.append({"outcome":label,"coef":f.params["combine_movement"],"ci_low":ci[0],"ci_high":ci[1],"p":f.pvalues["combine_movement"],"n":len(data)})
    print(label, f"{f.params['combine_movement']:+.3f}", f"({ci[0]:+.3f}, {ci[1]:+.3f})", "p", f"{f.pvalues['combine_movement']:.3g}", "n", len(data))
combine_df = pd.DataFrame(combine_rows)

# Position-specific Combine -> performance models.
print("\nBy position:")
pos_rows = []
for group in ["DL", "WR", "OL", "TE"]:
    sub = perf_sample[perf_sample["position_group"] == group]
    f = smf.ols("perf_z ~ combine_movement + B_draft + C(season_c)", data=sub).fit(
        cov_type="cluster", cov_kwds={"groups": sub["nfl_id"]}
    )
    ci = f.conf_int().loc["combine_movement"]
    pos_rows.append({"position_group": group, "coef": f.params["combine_movement"],
                     "ci_low": ci[0], "ci_high": ci[1], "p": f.pvalues["combine_movement"],
                     "n": len(sub)})
    print(group, f"{f.params['combine_movement']:+.3f}", f"({ci[0]:+.3f}, {ci[1]:+.3f})",
          "p", f"{f.pvalues['combine_movement']:.3g}", "n", len(sub))
position_df = pd.DataFrame(pos_rows)
print(position_df.round(3).to_string(index=False))
'''

code_figs = "LABELS = " + repr(LABELS) + "\n" + r'''
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, BASELINE, SURFACE, INK, SECONDARY = "#2a78d6","#eb6834","#1baf7a","#898781","#c3c2b7","#fcfcfb","#0b0b0b","#52514e"
plt.rcParams.update({"figure.facecolor":SURFACE,"axes.facecolor":SURFACE,"font.size":10,
                     "axes.spines.top":False,"axes.spines.right":False,"grid.color":"#e1e0d9",
                     "axes.edgecolor":BASELINE,"axes.linewidth":0.8,
                     "xtick.color":GRAY,"ytick.color":GRAY,"axes.labelcolor":SECONDARY})
from statistics import NormalDist
NORMAL = NormalDist()
RNG = np.random.default_rng(42)

def _cboot(frame, col, cluster="nfl_id", n=1200):
    groups=[g[col].dropna().to_numpy() for _,g in frame.groupby(cluster) if g[col].notna().any()]
    if len(groups) < 3:
        return (np.nan, np.nan)
    draws=[]
    for _ in range(n):
        idx=RNG.integers(0,len(groups),len(groups))
        draws.append(np.concatenate([groups[i] for i in idx]).mean())
    return tuple(np.percentile(draws,[2.5,97.5]))

def _ord(v):
    n=int(round(v)); suf="th" if 10 <= n%100 <= 20 else {1:"st",2:"nd",3:"rd"}.get(n%10,"th")
    return f"{n}{suf}"

def _pct(z): return 100*NORMAL.cdf(z)

def _title(ax,title,sub):
    ax.set_title(title,loc="left",fontsize=12.5,color=INK,pad=24)
    ax.text(0.0,1.015,sub,transform=ax.transAxes,ha="left",va="bottom",fontsize=9.5,color=SECONDARY)

# Figure 1: the Combine signal moves performance, not playing time.
pf=smf.ols("perf_z ~ combine_movement + B_draft + C(position_group) + C(season_c)",data=perf_sample).fit(cov_type="cluster",cov_kwds={"groups":perf_sample["nfl_id"]})
rf=smf.ols("role_z ~ combine_movement + B_draft + C(position_group) + C(season_c)",data=role_sample).fit(cov_type="cluster",cov_kwds={"groups":role_sample["nfl_id"]})
gname=["Bottom third","Middle third","Top third"]
fig,ax=plt.subplots(figsize=(7.4,4.3)); xs=np.arange(3)
for fit,data,label,color,off in [(pf,perf_sample,"Performance",BLUE,12),(rf,role_sample,"Playing time",ORANGE,-12)]:
    d=data.copy(); d["partial"]=fit.resid+fit.params["combine_movement"]*d["combine_movement"]
    d["third"]=pd.qcut(d["combine_movement"],3,labels=gname)
    means=[]; los=[]; his=[]
    for g in gname:
        sub=d[d["third"]==g]; m=sub["partial"].mean(); lo,hi=_cboot(sub,"partial")
        means.append(_pct(m)); los.append(_pct(lo)); his.append(_pct(hi))
    means=np.array(means); los=np.array(los); his=np.array(his)
    ax.plot(xs,means,color=color,lw=1.8,zorder=2)
    ax.errorbar(xs,means,yerr=[means-los,his-means],fmt="o",color=color,ecolor=color,
                elinewidth=1.3,capsize=0,markersize=8,markeredgecolor=SURFACE,
                markeredgewidth=.8,zorder=3)
    ax.annotate(f"{label}\n{_ord(means[-1])}",(xs[-1],means[-1]),
                xytext=(12,off),textcoords="offset points",color=color,
                fontsize=9.5,va="center",fontweight="bold")
ax.axhline(50,color=BASELINE,lw=.9,zorder=1)
ax.set_xticks(xs); ax.set_xticklabels(["Bottom\nthird","Middle\nthird","Top\nthird"])
ax.set_xlim(-0.28,2.78); ax.set_ylim(34,66); ax.set_yticks([35,40,45,50,55,60,65])
ax.set_xlabel("Combine movement"); ax.set_ylabel("Adjusted percentile (50 = average)")
ax.grid(axis="y",alpha=.7)
ax.text(0.0,-0.24,f"{len(perf_sample)} player-seasons with performance data; {len(role_sample)} with playing-time data.",
        transform=ax.transAxes,ha="left",va="top",fontsize=8.5,color=GRAY)
_title(ax,LABELS["fig1_title"],LABELS["fig1_subtitle"])
fig.savefig(FIG/"combine_linkage.png",dpi=180,bbox_inches="tight"); plt.show()

# Figure 4: three facets, one per driver.
order=["DL","WR","OL","TE","DB"]
pos=pos_df.set_index("position").reindex([p for p in order if p in pos_df["position"].values]).reset_index()
fig,axes=plt.subplots(1,3,figsize=(9.6,4.6),sharey=True); yy=np.arange(len(pos))
for ax,(key,label,color,xlim) in zip(axes,[("role","Current playing time",ORANGE,(0.2,0.9)),
                                           ("draft","Draft position",AQUA,(-0.25,2.95)),
                                           ("perf","Performance",BLUE,(-0.4,0.45))]):
    c=pos[key].to_numpy(float); lo=pos[key+"_lo"].to_numpy(float); hi=pos[key+"_hi"].to_numpy(float)
    mask=np.isfinite(c)&np.isfinite(lo)&np.isfinite(hi)
    ax.errorbar(c[mask],yy[mask],xerr=[c[mask]-lo[mask],hi[mask]-c[mask]],fmt="o",
                color=color,ecolor=color,elinewidth=1.2,capsize=0,markersize=7,
                markeredgecolor=SURFACE,markeredgewidth=.6,zorder=3)
    for yi,v in zip(yy[mask],c[mask]):
        ax.annotate(f"{v:+.2f}",(v,yi),xytext=(0,9),textcoords="offset points",
                    ha="center",fontsize=8.2,color=SECONDARY)
    if key=="perf":
        for yi in yy[~mask]:
            ax.text(0,yi,"not measurable",ha="center",va="center",fontsize=8.2,
                    color=GRAY,style="italic",
                    bbox=dict(facecolor=SURFACE,edgecolor="none",pad=1.5))
    ax.axvline(0,color=BASELINE,lw=.9,zorder=1); ax.set_xlim(*xlim)
    ax.set_title(label,loc="left",fontsize=11,color=INK,pad=8); ax.grid(axis="x",alpha=.7)
axes[0].set_yticks(yy)
axes[0].set_yticklabels([f"{p} ({int(n)})" for p,n in zip(pos["position"],pos["n"])])
axes[0].invert_yaxis(); axes[1].set_xlabel("Effect on next-season playing time (SD; 95% CI)")
fig.suptitle(LABELS["fig4_title"],x=.01,y=.995,ha="left",fontsize=12.5,color=INK)
fig.text(.01,.952,LABELS["fig4_subtitle"],ha="left",va="top",fontsize=9.5,color=SECONDARY)
fig.tight_layout(rect=[0,0,1,.89])
fig.savefig(FIG/"next_role_forest.png",dpi=180,bbox_inches="tight"); plt.show()

# Figure 5: snaps persist; a better season does not earn more snaps.
def _qrows(frame,xcol,ycol,nq=5):
    f=frame.copy(); f["_q"]=pd.qcut(f[xcol],nq,labels=False)
    rows=[]
    for _,sub in f.groupby("_q"):
        rows.append((sub[ycol].mean(),*_cboot(sub,ycol)))
    return np.array(rows)
base5=base[base["next_role"].notna() & (base["perf_n"]>=50)].copy()
fig,axes=plt.subplots(1,2,figsize=(9.6,4.3)); xs=np.arange(5)
for ax,frame,xcol,ycol,title,xlabel,ylabel,color,ntext,slope in [
    (axes[0],base5,"role_z","next_role","Current snaps → next season",
     "Playing time quintile\n(low → high)","Next-season playing time (SD)",
     ORANGE,"n=192","model: +0.61 per SD"),
    (axes[1],diff,"d_perf","d_role","Change in performance → change in snaps",
     "Change in performance quintile\n(worst → best)","Change in playing time (SD)",
     BLUE,"n=235","model: −0.10 (p=0.11)")]:
    rows=_qrows(frame,xcol,ycol); y=rows[:,0]; lo=rows[:,1]; hi=rows[:,2]
    ax.axhline(0,color=BASELINE,lw=.9,zorder=1); ax.plot(xs,y,color=color,lw=1.5,zorder=2)
    ax.errorbar(xs,y,yerr=[y-lo,hi-y],fmt="o",color=color,ecolor=color,
                elinewidth=1.2,capsize=0,markersize=7,markeredgecolor=SURFACE,
                markeredgewidth=.7,zorder=3)
    ax.annotate(f"{y[-1]:+.2f}",(xs[-1],y[-1]),xytext=(8,0),textcoords="offset points",
                va="center",fontsize=9.5,color=color,fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels(["1","2","3","4","5"])
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_ylim(-.6,1.5)
    ax.set_title(title,loc="left",fontsize=10.5,color=INK,pad=8); ax.grid(axis="y",alpha=.7)
    ax.text(.02,.96,ntext,transform=ax.transAxes,ha="left",va="top",fontsize=9,color=GRAY)
    ax.text(.02,.89,slope,transform=ax.transAxes,ha="left",va="top",fontsize=8.5,color=SECONDARY)
fig.suptitle(LABELS["fig5_title"],x=.01,y=.995,ha="left",fontsize=12.5,color=INK)
fig.text(.01,.952,LABELS["fig5_subtitle"],ha="left",va="top",fontsize=9.5,color=SECONDARY)
fig.tight_layout(rect=[0,0,1,.89])
fig.savefig(FIG/"persistence_within_player.png",dpi=180,bbox_inches="tight"); plt.show()

# Supporting check: the performance null survives playing-time measure choices.
fig, ax = plt.subplots(figsize=(8, 4))
models = list(dict.fromkeys(sens_df["model"]))
ypos = {m:i for i,m in enumerate(models)}
for series, color, off in [("role",BLUE,-.18),("performance",ORANGE,0),("draft",AQUA,.18)]:
    sub = sens_df[sens_df["series"] == series]
    label = "playing time" if series == "role" else series
    ax.errorbar(sub["coef"], [ypos[m]+off for m in sub["model"]],
                xerr=[sub["coef"]-sub["lo"], sub["hi"]-sub["coef"]],
                fmt="o", color=color, ecolor=color, capsize=0, markersize=6, label=label)
ax.axvline(0, color=BASELINE, lw=.8); ax.set_yticks(range(len(models)))
ax.set_yticklabels(models); ax.invert_yaxis()
ax.set_xlabel("Coefficient for next-season playing time (z; 95% CI)")
ax.legend(frameon=False, fontsize=8)
ax.set_title("The performance null survives playing-time measure choices", loc="left")
fig.savefig(FIG/"role_sensitivity.png",dpi=180,bbox_inches="tight"); plt.show()

# Supporting check: the tails of the playing-time gap.
tail_plot=tail[tail["allocation"]!="mid"]
fig,ax=plt.subplots(figsize=(6.6,3.8))
for label,color in [("high role / low performance",ORANGE),("low role / high performance",BLUE)]:
    sub=tail_plot[tail_plot["allocation"]==label]
    ax.scatter(sub["perf_z"],sub["role_gap"],s=36,c=color,edgecolors=SURFACE,
               linewidths=.5,label=label.replace("role","snaps"))
ax.axhline(0,color=BASELINE,lw=.8); ax.axvline(0,color=BASELINE,lw=.8)
ax.set_xlabel("Performance (z)"); ax.set_ylabel("Playing-time gap")
ax.legend(frameon=False,fontsize=7)
ax.set_title("Playing time is not allocated to measured performance",loc="left")
fig.savefig(FIG/"role_gap_tails.png",dpi=180,bbox_inches="tight"); plt.show()
'''

md_salary_intro = """## Dollar layer: cost efficiency and the rent proxy

The salary panel merges OverTheCap positional cap spending (2023–2025), nflverse snaps/rosters/stats/schedules, and the 2025 archived OTC team cap ledger. The panel is embedded below as a compressed CSV so this notebook is self-contained. The derivation and source notes are in the repository (`src/salary/`, `docs/EXTERNAL_DATA.md`, `docs/SOCCER_DATA.md`). All models are observational; the rent residual is a cap-allocation residual, not a causal rent.
"""

code_salary_data = f'''
import base64, zlib, io
SALARY_B64 = "{SALARY_B64}"
RENT_B64 = "{RENT_B64}"
SOCCER_B64 = "{SOCCER_B64}"
panel = pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(SALARY_B64)).decode()))
rent_quartiles = pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(RENT_B64)).decode()))
soccer = pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(SOCCER_B64)).decode()))
print("salary panel:", panel.shape, "| seasons:", sorted(panel.season.unique()))
print("rent quartiles:", rent_quartiles.shape)
panel.head()
'''

code_salary_models = r'''
def salfit(formula, data):
    cols = [c for c in data.columns if c in formula] + ["team"]
    data = data.dropna(subset=cols).copy()
    return smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": data["team"]})

specs = {
    "star": "star_share + log_payroll + C(season_c)",
    "rookie_homegrown": "rookie_snap_share + homegrown_snap_share + log_payroll + C(season_c)",
    "joint": "star_share + youth_snap_share + homegrown_snap_share + log_payroll + C(season_c)",
}
rows = []
for outcome in ["wins", "point_diff", "off_epa_per_play", "wins_per_100m"]:
    for spec, rhs in specs.items():
        m = salfit(f"{outcome} ~ {rhs}", panel)
        for term in m.params.index:
            if term.startswith("C(") or term == "Intercept":
                continue
            ci = m.conf_int().loc[term]
            rows.append({"outcome": outcome, "spec": spec, "term": term,
                         "coef": m.params[term], "ci_low": ci[0], "ci_high": ci[1],
                         "p": m.pvalues[term], "n": int(m.nobs)})
salary_results = pd.DataFrame(rows)
print("Salary models (wins):")
print(salary_results.query("outcome == 'wins'")[["spec", "term", "coef", "ci_low", "ci_high", "p", "n"]].round(3).to_string(index=False))

q = salfit("wins ~ qb_share + I(qb_share**2) + log_payroll + C(season_c)", panel)
q2 = [k for k in q.params.index if k.startswith("I(")][0]
print("\nQB quadratic (wins):")
print(f"  linear {q.params['qb_share']:+.2f} (p={q.pvalues['qb_share']:.3f})")
print(f"  quadratic {q.params[q2]:+.2f} (p={q.pvalues[q2]:.3f})")
print(f"  inflection at QB share = {(-q.params['qb_share']/(2*q.params[q2])):.3f}")

print("\nRent by efficiency quartile ($M per team):")
print(rent_quartiles.round(2).to_string(index=False))

print("\nSoccer comparison (illustrative):")
print(soccer[["club", "league", "season", "position", "wage_measure", "revenue_measure", "wage_revenue_ratio"]].to_string(index=False))
'''

code_salary_figs = r'''
# Figure 2: star spending flat; rookie and homegrown snaps move.
def _qrows4(frame,xcol,ycol,cluster="team",nq=4):
    f=frame.copy(); f["_q"]=pd.qcut(f[xcol],nq,labels=False)
    rows=[]
    for _,sub in f.groupby("_q"):
        lo,hi=_cboot(sub,ycol,cluster,800); rows.append((sub[xcol].mean(),sub[ycol].mean(),lo,hi))
    return np.array(rows)
fig,axes=plt.subplots(1,3,figsize=(9.6,4.2),sharey=True)
for ax,(col,title,xlabel,color) in zip(axes,[("star_share","Star spending","Star spending (% of cap)",ORANGE),
                                             ("rookie_snap_share","Rookie snaps","Rookie snap share (%)",AQUA),
                                             ("homegrown_snap_share","Homegrown snaps","Homegrown snap share (%)",AQUA)]):
    rows=_qrows4(panel,col,"wins_per_100m")
    x=rows[:,0]*100; y=rows[:,1]; lo=rows[:,2]; hi=rows[:,3]
    ax.plot(x,y,color=color,lw=1.5,zorder=2)
    ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt="o",color=color,ecolor=color,elinewidth=1.2,
                capsize=0,markersize=7,markeredgecolor=SURFACE,markeredgewidth=.7,zorder=3)
    ax.annotate(f"{y[-1]:.1f}",(x[-1],y[-1]),xytext=(7,9),textcoords="offset points",
                fontsize=9,color=color,fontweight="bold")
    change=y[-1]-y[0]; ctxt="0.0" if abs(change)<0.05 else f"{change:+.1f}".replace("-","−")
    ax.text(.98,.96,f"Q4 − Q1: {ctxt}",transform=ax.transAxes,ha="right",va="top",
            fontsize=9,color=SECONDARY,bbox=dict(facecolor=SURFACE,edgecolor="none",pad=1.5))
    ax.set_title(title,loc="left",fontsize=11,color=INK,pad=8); ax.set_xlabel(xlabel); ax.grid(axis="y",alpha=.7)
axes[0].set_ylabel("Wins per $100M"); axes[0].set_ylim(3.0,5.6)
fig.suptitle(LABELS["fig2_title"],x=.01,y=.995,ha="left",fontsize=12.5,color=INK)
fig.text(.01,.952,LABELS["fig2_subtitle"],ha="left",va="top",fontsize=9.5,color=SECONDARY)
fig.tight_layout(rect=[0,0,1,.89])
fig.savefig(FIG/"salary_efficiency.png",dpi=180,bbox_inches="tight"); plt.show()

# Figure 3: one quarterback panel with an honest band.
qd=panel.dropna(subset=["wins","qb_share","log_payroll","season_c"]).copy()
qf=smf.ols("wins ~ qb_share + I(qb_share**2) + log_payroll + C(season_c)",data=qd).fit(
    cov_type="cluster",cov_kwds={"groups":qd["team"]})
q2=[k for k in qf.params.index if k.startswith("I(")][0]
b1,b2=float(qf.params["qb_share"]),float(qf.params[q2])
partial=qf.resid+b1*qd["qb_share"]+b2*qd["qb_share"]**2
xbar=float(qd["qb_share"].mean()); xbar2=float((qd["qb_share"]**2).mean()); baseq=float(partial.mean())
xs=np.linspace(float(qd["qb_share"].min()),float(qd["qb_share"].max()),120)
curve=baseq+b1*(xs-xbar)+b2*(xs**2-xbar2)
cov=qf.cov_params().loc[["qb_share",q2],["qb_share",q2]].to_numpy()
draws=RNG.multivariate_normal(np.array([b1,b2]),cov,size=1500)
curves=baseq+draws[:,0][:,None]*(xs[None,:]-xbar)+draws[:,1][:,None]*(xs[None,:]**2-xbar2)
blo,bhi=np.percentile(curves,[2.5,97.5],axis=0)
infl=-b1/(2*b2)
fig,ax=plt.subplots(figsize=(7.4,4.5))
ax.scatter(qd["qb_share"]*100,partial,s=16,c=GRAY,alpha=.55,edgecolors=SURFACE,linewidths=.35,zorder=2)
ax.fill_between(xs*100,blo,bhi,color=ORANGE,alpha=.15,lw=0,zorder=1)
ax.plot(xs*100,curve,color=ORANGE,lw=2.0,zorder=3)
ax.axvline(infl*100,color=ORANGE,lw=1.0,ls="--",zorder=1)
ytop=float(np.nanmax(partial))+0.8; ax.set_xlim(0,max(xs*100)+1); ax.set_ylim(float(np.nanmin(partial))-0.8,ytop)
ax.annotate(f"fitted turning point ≈{infl*100:.0f}%",(infl*100,ytop),xytext=(6,-12),
            textcoords="offset points",fontsize=9,color=ORANGE)
ax.text(.02,.05,"shaded band: 95% (clustered covariance); vertex not statistically identified",transform=ax.transAxes,
        ha="left",va="bottom",fontsize=8.5,color=SECONDARY,
        bbox=dict(facecolor=SURFACE,edgecolor="none",pad=2))
ax.set_xlabel("QB share of offense+defense cap spending (%)")
ax.set_ylabel("Wins, adjusted for payroll and season"); ax.grid(axis="y",alpha=.7)
_title(ax,LABELS["fig3_title"],LABELS["fig3_subtitle"])
fig.savefig(FIG/"qb_premium.png",dpi=180,bbox_inches="tight"); plt.show()

# Figure 6: overpay by 2025 efficiency quartile.
rq=rent_quartiles; xx=np.arange(len(rq))
star=rq["star_rent_m"].to_numpy(float); under=rq["under_rent_m"].to_numpy(float)
fig,ax=plt.subplots(figsize=(7.4,4.4))
ax.bar(xx,star,width=.58,color=GRAY,edgecolor=SURFACE,linewidth=1.5,label="Star cap dollars",zorder=2)
ax.bar(xx,under,width=.58,bottom=star,color=ORANGE,edgecolor=SURFACE,linewidth=1.5,
       label="Underperformers",zorder=2)
for xi,total in zip(xx,star+under):
    ax.annotate(f"${total:.0f}M",(xi,total),xytext=(0,6),textcoords="offset points",
                ha="center",va="bottom",fontsize=9.5,color=INK)
ax.set_xticks(xx); ax.set_xticklabels(["Q1\nleast efficient","Q2","Q3","Q4\nmost efficient"])
ax.set_xlabel("2025 efficiency quartile (wins per $100M)")
ax.set_ylabel("$M per team above the pay model"); ax.set_ylim(0,82); ax.grid(axis="y",alpha=.7)
ax.text(3.42,80,"Most vs least efficient\nTotal −$20.5M (−$40.9M to −$2.0M)\nUnderperformers −$6.3M (−$14.5M to −$0.2M)",
        ha="right",va="top",fontsize=8.5,color=SECONDARY,linespacing=1.35)
ax.legend(loc="upper left",fontsize=8.5)
_title(ax,LABELS["fig6_title"],LABELS["fig6_subtitle"])
fig.savefig(FIG/"overpay_quartiles.png",dpi=180,bbox_inches="tight"); plt.show()
'''

md_salary_appendix = """## Salary appendix: sources and limits

- **OTC positional spending** (2023–2025) is the primary star-share measure. It is cap spending by position, not a full cap ledger.
- **Archived OTC 2025 team cap pages** supply the player-level 2025 active-roster cap numbers. The 32-team snapshot matches 98% of snaps. The rent sample covers 909 players and 69% of active-cap dollars; offensive linemen and specialists are excluded because the public data have no individual performance measure.
- **nflverse** supplies snaps, rosters, stats, and schedules. Player performance is standardized within position group and season; minimums are 100 QB dropbacks, 50 RB touches, 30 WR/TE targets, and 8 games for defensive players.
- **Rent** is a positive pay-performance residual from log 2025 cap number on performance z, age, experience, and position. It is a cap-allocation residual, not a causal rent: cap hits reflect signing-bonus proration, restructures, timing, and expected future performance.
- **Soccer** uses UEFA 2025, Deloitte Money League 2025, club annual reports, and official league tables. Accounting scopes and season windows differ; the table is illustrative, not a natural experiment.

Full source notes: `docs/EXTERNAL_DATA.md` and `docs/SOCCER_DATA.md` in the repository.
"""

md_weekly = """## Week-to-week check

The season-level result is robust, but it is not a single-week trigger. Using the same tracking data, next-week role is predicted by this-week role, not by this-week performance. Early-season performance also does not predict late-season role after controlling for early role. The result supports a 4–6 week rolling role review, not an automated weekly decision. The result table is embedded below; the derivation is in `src/discovery/weekly_role.py`.
"""

code_weekly = f'''
import base64, zlib, io
WEEKLY_B64 = "{WEEKLY_B64}"
weekly = pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(WEEKLY_B64)).decode()))
print("Weekly lead-lag (next-week role):")
print(weekly.query("model == 'weekly_lead_lag'")[["term", "coef", "ci_low", "ci_high", "p", "n"]].round(3).to_string(index=False))
print("\\nEarly-season -> late-season role:")
print(weekly.query("model == 'early_late'")[["term", "coef", "ci_low", "ci_high", "p", "n"]].round(3).to_string(index=False))
'''

md_appendix = """## Formal appendix: what is identified

- **Combine linkage:** a 10 Hz Combine movement composite is tested against the tracking-derived performance residual. The coefficient is positive and precise; the same composite does not predict role or the role gap.
- **Role persistence:** next-season role is modeled as a function of current role, the performance residual, draft capital, position, and season, with cluster-robust standard errors. The performance coefficient is near zero; the role and draft-capital coefficients are positive. Leave-one-player-out R² and within-player changes are reported as validation.
- **What is not identified:** causal effects of coaches, teams, schemes, injuries, or contracts. Role is snaps per appearance, not full depth-chart share. The role gap is a diagnostic, not a verdict on individual players. The DB performance residual is unidentifiable (reliability 0.12) and is excluded from pooled models.
- **RJF/Xenotechnics:** the Yellow Square/Möbius lenses are treated as hypotheses. They return wide nulls; the residual finding is the allocation layer. No intent or suppression is claimed.
"""

md_repro = """## Reproduce

- Data: NFL Big Data Bowl 2027, CC BY-NC 4.0. On Kaggle the notebook reads `/kaggle/input/nfl-big-data-bowl-2027/`; locally it reads `data/raw`.
- Salary panel: embedded as a compressed CSV derived from public OverTheCap positional spending (2023–2025), nflverse snaps/rosters/stats/schedules, and archived OTC 2025 team cap pages. The derivation is in `src/salary/`; sources and limits are in `docs/EXTERNAL_DATA.md`.
- Week-to-week check: embedded result table derived from the weekly tracking residuals; the derivation is in `src/discovery/weekly_role.py`.
- Main text: `writeup/submission.md`.
- Figures are written to `figures/`.
- The analysis is observational; see the limitations in the writeup.
"""

nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
# ---------------------------------------------------------------------------
# Cost-risk rebuild overrides (keep the notebook consistent with the writeup)
# ---------------------------------------------------------------------------
FIG_NAMES = [
    "combine_linkage.png",
    "net_rent.png",
    "next_role_forest.png",
    "persistence_within_player.png",
    "allocation_gap.png",
]
FIG_B64 = {
    name: base64.b64encode((ROOT / "writeup" / "figures" / name).read_bytes()).decode()
    for name in FIG_NAMES
}

def _csv_b64(path: Path) -> str:
    csv = pd.read_csv(path).to_csv(index=False)
    return base64.b64encode(zlib.compress(csv.encode())).decode()

NET_RENT_B64 = _csv_b64(SAL / "net_rent_groups.csv")
PAY_NESTED_B64 = _csv_b64(SAL / "pay_model_nested.csv")
GAP_GROUPS_B64 = _csv_b64(ROOT / "outputs" / "discovery" / "allocation_gap_groups.csv")
GAP_TAILS_B64 = _csv_b64(ROOT / "outputs" / "discovery" / "allocation_gap_tails.csv")

md_intro = """# The testing is informative; the decisions are not

**NFL Big Data Bowl 2027 — public analysis notebook**

This notebook reproduces the core competition-data results: the 10 Hz Combine movement composite, position-specific performance models, role persistence, and the week-to-week check. The cost-risk tables are derived public-data aggregates embedded for self-containment; the writeup and repository carry the full derivation.

- **The Combine signal is position-specific.** DL +0.734 (95% CI 0.461–1.007), WR +0.366 (p=0.084), OL +0.058, TE +0.093; interaction p=0.0004. The pooled +0.299 is a defensive-line result; the standardized effect is 0.185, not one-third.
- **Playing time is sticky and draft-driven.** Next-season role follows current role (+0.606) and draft capital (+0.785), not performance (−0.011); the within-player change is −0.095 (p=0.11).
- **The cap pays for status.** Signed net rent: stars about +$6.3M, young high performers −$1.1M; the nested pay model's performance coefficient falls from +0.128 to +0.040 once role and draft enter.
- **The allocation gap is systematic.** Performance minus role: late picks/UDFAs +0.59, early picks −0.92 in the full 233-row sample; the strict top-performance/bottom-role quartile tail is 13 player-seasons.
- **All analyses are exploratory/post-hoc.** The preregistered RJF/Yellow Square null pattern is in the repository appendix. Competition data is CC BY-NC 4.0; do not redistribute.

Self-contained reconstruction: Combine +0.295 (p<0.001), role −0.034 (n=195); full pipeline +0.299 and −0.019 (n=192). The small differences come from the reconstruction's role-standardization universe, not sampling variation.
"""

code_figs = f"""
import base64
from IPython.display import Image, display
FIG_B64 = {repr(FIG_B64)}
for name, b64 in FIG_B64.items():
    print(name)
    display(Image(data=base64.b64decode(b64)))
"""

md_cost_risk = """## Cost-risk layer: signed net rent and the allocation gap

The 2025 cap ledger is modeled on performance, age, experience, and position. We report the **signed** residual — dollars above or below the model, netted across over- and under-payments — not a positive-part sum. The nested model adds snap share and draft capital. The allocation gap is performance z minus role z, both within position and season. These are derived public-data aggregates embedded for self-containment; the full derivation is in `src/discovery/cost_risk.py` and `src/salary/rents.py`. All analyses are exploratory.
"""

code_cost_risk = f"""
import base64, zlib, io
def _load(b64):
    return pd.read_csv(io.StringIO(zlib.decompress(base64.b64decode(b64)).decode()))
net_rent = _load("{NET_RENT_B64}")
pay_nested = _load("{PAY_NESTED_B64}")
gap_groups = _load("{GAP_GROUPS_B64}")
gap_tails = _load("{GAP_TAILS_B64}")
print("Signed net rent by group ($M):")
print(net_rent.round(2).to_string(index=False))
print("\\nNested pay model (performance coefficient):")
print(pay_nested.round(3).to_string(index=False))
print("\\nAllocation gap by draft quartile:")
print(gap_groups.round(2).to_string(index=False))
print("\\nAllocation gap tails:")
print(gap_tails.round(2).to_string(index=False))
"""

md_salary_appendix = """## Cost-risk appendix: sources and limits

- **OTC positional spending** (2023–2025) and the archived 2025 OTC active-roster cap pages are the salary sources; nflverse supplies snaps, rosters, stats, and schedules.
- The 2025 cap snapshot matches 99.3% of active-cap dollars to a 2025 snap on player ID and team. The 909-player rent sample covers 68.7% of active-cap dollars; offensive linemen and specialists are excluded.
- **Net rent** is the signed residual from log 2025 cap number on performance, age, experience, and position. It is an accounting residual, not a causal rent: cap hits reflect proration, restructures, timing, and expected future performance. The nested model adds snap share and draft capital; draft capital is partly the rookie wage scale.
- The allocation gap is descriptive; the strict tail is 12 players. The salary performance measure is nflverse public production, not the NGS `player_play` residual.
- **Soccer** uses UEFA 2025, Deloitte Money League 2025, club annual reports, and official league tables; accounting scopes and season windows differ. The table is illustrative, not a natural experiment.

Full source notes: `docs/EXTERNAL_DATA.md` and `docs/SOCCER_DATA.md`.
"""

md_weekly = """## Week-to-week check

Next-week role is predicted by this-week role, not by this-week performance. Early-season performance also does not predict late-season role after controlling for early role. The data do not identify an optimal review cadence; a monthly review is a process choice, not a tested rule. The result table is embedded below; the derivation is in `src/discovery/weekly_role.py`.
"""

md_appendix = """## Formal appendix: what is identified

- **Combine linkage:** the 10 Hz movement composite is tested against the tracking-derived performance residual. The pooled coefficient is positive, but position-specific models show it is a defensive-line result: DL +0.734, WR +0.366 (p=0.084), OL +0.058, TE +0.093; interaction p=0.0004. The DL outcome is get-off.
- **Role persistence:** next-season role is modeled as a function of current role, the performance residual, draft capital, position, and season, with cluster-robust standard errors. The performance coefficient is near zero; role and draft capital are positive. Leave-one-player-out R² and within-player changes are reported as validation.
- **Cost-risk:** signed net rent and the performance-role gap are exploratory. The predictability lens does not survive role controls.
- **What is not identified:** causal effects of coaches, teams, schemes, injuries, or contracts. Role is snaps per appearance, not full depth-chart share. The role gap is a diagnostic. DB performance is unidentifiable and excluded from pooled models.
"""

nb["cells"] = [
    nbf.v4.new_markdown_cell(md_intro),
    nbf.v4.new_code_cell(code_setup),
    nbf.v4.new_markdown_cell("## Position-specific performance residuals"),
    nbf.v4.new_code_cell(code_perf),
    nbf.v4.new_markdown_cell("## Player-season role panel"),
    nbf.v4.new_code_cell(code_panel),
    nbf.v4.new_markdown_cell("## Role persistence and within-player validation"),
    nbf.v4.new_code_cell(code_models),
    nbf.v4.new_markdown_cell("## 10 Hz Combine movement linkage"),
    nbf.v4.new_code_cell(code_combine),
    nbf.v4.new_markdown_cell("## Figures"),
    nbf.v4.new_code_cell(code_figs),
    nbf.v4.new_markdown_cell(md_cost_risk),
    nbf.v4.new_code_cell(code_cost_risk),
    nbf.v4.new_markdown_cell(md_weekly),
    nbf.v4.new_code_cell(code_weekly),
    nbf.v4.new_markdown_cell(md_salary_appendix),
    nbf.v4.new_markdown_cell(md_appendix),
    nbf.v4.new_markdown_cell(md_repro),
]
OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUT)
print(OUT)
