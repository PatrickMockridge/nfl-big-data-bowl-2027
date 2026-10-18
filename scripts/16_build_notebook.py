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

md_intro = """# The Allocation Gap: The Combine Signal Is Real; the Depth Chart and the Cap Ignore It

**NFL Big Data Bowl 2027 — public analysis notebook**

**What is new**

- The 10 Hz Combine signal predicts performance (**+0.299 SD/SD**) but not role (**−0.019**).
- Next-season role follows current role (**+0.606**) and draft capital (**+0.785**), not performance (**−0.011**); the within-player change is **−0.095** (p = 0.11).
- The weekly check: next-week role follows this-week role (**+0.753**); this-week performance does not (**−0.006**, p = 0.59).
- The cap repeats the pattern: star share **−0.70** (p = 0.89); rookie snap share **−28.4** (p = 0.004); homegrown **+9.2** (p = 0.001); QB spending flattens at about **14% of payroll**.
- The binding constraint is not measurement; it is allocation.

The Yellow Square/Möbius lenses were wide nulls; the residual is the allocation layer. This notebook reproduces the robust core from the raw competition data plus a self-contained salary panel and a week-to-week check derived from public OverTheCap and nflverse data. It uses the 10 Hz Combine tracking and the tracking-derived Next Gen Stats in `player_play`. Competition data is CC BY-NC 4.0; do not redistribute.
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
        pos_rows.append({"position":g,
                         "role":f.params["role_z"],"role_lo":f.conf_int().loc["role_z",0],"role_hi":f.conf_int().loc["role_z",1],
                         "perf":np.nan,"perf_lo":np.nan,"perf_hi":np.nan,
                         "draft":f.params["B_draft"],"draft_lo":f.conf_int().loc["B_draft",0],"draft_hi":f.conf_int().loc["B_draft",1]})
    else:
        sub = sub.dropna(subset=["role_z","perf_z","B_draft","next_role"])
        f = fit("next_role ~ role_z + perf_z + B_draft", sub)
        pos_rows.append({"position":g,
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
                      "path_eff":dist[-1]/path if path>0 else np.nan})
att = g.apply(attempt_stats, include_groups=False).reset_index()
att = att.merge(ct[["event_id","nfl_id","attempt","drill_name"]].drop_duplicates(), on=["event_id","nfl_id","attempt"], how="left")
for col in ["max_speed","max_accel_first","time_to_1yd","path_eff"]:
    att[col]=att.groupby("drill_name")[col].transform(lambda x:(x-x.mean())/x.std(ddof=0) if x.std(ddof=0)>0 else x*0)
cm = att.groupby("nfl_id").agg(speed=("max_speed","mean"),accel=("max_accel_first","mean"),
                               time1=("time_to_1yd","mean"),path=("path_eff","mean")).reset_index()
z = cm[["speed","accel","path"]].apply(lambda x:(x-x.mean())/x.std(ddof=0))
cm["combine_movement"] = pd.concat([z, -cm["time1"]], axis=1).mean(axis=1)
print("Combine movement players:", len(cm))

perf_sample = ps.merge(cm, on="nfl_id", how="left").dropna(subset=["combine_movement","perf_z"])
perf_sample = perf_sample[perf_sample["position_group"] != "DB"].copy()
role_sample = base.merge(cm, on="nfl_id", how="left").dropna(subset=["combine_movement"])
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
'''

code_figs = r'''
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, BASELINE, SURFACE, INK = "#2a78d6","#eb6834","#1baf7a","#898781","#c3c2b7","#fcfcfb","#0b0b0b"
plt.rcParams.update({"figure.facecolor":SURFACE,"axes.facecolor":SURFACE,"font.size":9,
                     "axes.spines.top":False,"axes.spines.right":False,"grid.color":"#e1e0d9"})

# Combine linkage.
fig, ax = plt.subplots(figsize=(7.2, 3.0))
cf = combine_df.iloc[::-1].reset_index(drop=True)
for i, row in cf.iterrows():
    color = BLUE if row["ci_low"] > 0 else ORANGE
    ax.errorbar(row["coef"], i, xerr=[[row["coef"]-row["ci_low"]],[row["ci_high"]-row["coef"]]],
                fmt="o", color=color, ecolor=color, capsize=0, markersize=6)
    ax.annotate(f"n={int(row['n'])}", (row["ci_high"], i), xytext=(5,0), textcoords="offset points",
                va="center", fontsize=7, color=GRAY)
ax.axvline(0, color=BASELINE, lw=.8); ax.set_yticks(range(len(cf))); ax.set_yticklabels(cf["outcome"])
ax.set_xlabel("Coefficient per SD of Combine movement (95% CI)")
ax.set_title("Combine movement predicts performance, not role", loc="left")
fig.savefig(FIG/"combine_linkage.png",dpi=180,bbox_inches="tight"); plt.show()

# Next-role forest.
fig, ax = plt.subplots(figsize=(8, 4))
yy = np.arange(len(pos_df))
for key, label, color, off in [("role","Current role",BLUE,-.2),("perf","Performance",ORANGE,0),("draft","Draft capital",AQUA,.2)]:
    coef = pos_df[key].to_numpy(); lo = pos_df[key+"_lo"].to_numpy(); hi = pos_df[key+"_hi"].to_numpy()
    mask = ~np.isnan(coef)
    ax.errorbar(coef[mask], (yy+off)[mask], xerr=[(coef-lo)[mask],(hi-coef)[mask]],
                fmt="o", color=color, ecolor=color, capsize=0, markersize=6, label=label)
    if key == "perf":
        for idx in np.where(~mask)[0]:
            ax.text(0.02, yy[idx]+off, "unidentifiable", fontsize=6.5, color=GRAY, va="center")
ax.axvline(0, color=BASELINE, lw=.8); ax.set_yticks(yy); ax.set_yticklabels(pos_df["position"]); ax.invert_yaxis()
ax.set_xlabel("Coefficient for next-season role (z; 95% CI)"); ax.legend(frameon=False, fontsize=7)
ax.set_title("Role persists and follows draft capital, not performance", loc="left")
fig.savefig(FIG/"next_role_forest.png",dpi=180,bbox_inches="tight"); plt.show()

# Role-measure sensitivity.
fig, ax = plt.subplots(figsize=(8, 4))
models = list(dict.fromkeys(sens_df["model"]))
ypos = {m:i for i,m in enumerate(models)}
for series, color, off in [("role",BLUE,-.18),("performance",ORANGE,0),("draft",AQUA,.18)]:
    sub = sens_df[sens_df["series"] == series]
    ax.errorbar(sub["coef"], [ypos[m]+off for m in sub["model"]],
                xerr=[sub["coef"]-sub["lo"], sub["hi"]-sub["coef"]],
                fmt="o", color=color, ecolor=color, capsize=0, markersize=6, label=series)
ax.axvline(0, color=BASELINE, lw=.8); ax.set_yticks(range(len(models))); ax.set_yticklabels(models); ax.invert_yaxis()
ax.set_xlabel("Coefficient for next-season role (z; 95% CI)"); ax.legend(frameon=False, fontsize=7)
ax.set_title("The performance null survives role-measure choices", loc="left")
fig.savefig(FIG/"role_sensitivity.png",dpi=180,bbox_inches="tight"); plt.show()

# Role persistence vs performance.
fig, axes = plt.subplots(1,2,figsize=(9,3.8),sharey=True)
for ax,col,label,color in [(axes[0],"role_z","Current role (z)",BLUE),(axes[1],"perf_z","Performance (z)",ORANGE)]:
    ax.scatter(base[col],base["next_role"],s=14,c=GRAY,alpha=.45,edgecolors=SURFACE,linewidths=.3)
    coef=np.polyfit(base[col],base["next_role"],1); xs=np.linspace(base[col].min(),base[col].max(),50)
    ax.plot(xs,np.polyval(coef,xs),color=color,lw=1.5); ax.axhline(0,color=BASELINE,lw=.8)
    ax.set_xlabel(label); ax.set_title(label.split(" (")[0]+" to next role",loc="left")
    ax.annotate(f"slope {coef[0]:+.2f}",(0.04,.92),xycoords="axes fraction",fontsize=8)
axes[0].set_ylabel("Next-season role (z)")
fig.suptitle("Role persists; performance does not",x=.01,ha="left")
fig.tight_layout(); fig.savefig(FIG/"role_persistence.png",dpi=180,bbox_inches="tight"); plt.show()

# Within-player change.
fig,ax=plt.subplots(figsize=(6,4))
ax.scatter(diff["d_perf"],diff["d_role"],s=16,c=GRAY,alpha=.5,edgecolors=SURFACE,linewidths=.3)
coef=np.polyfit(diff["d_perf"],diff["d_role"],1); xs=np.linspace(diff["d_perf"].min(),diff["d_perf"].max(),50)
ax.plot(xs,np.polyval(coef,xs),color=ORANGE,lw=1.5); ax.axhline(0,color=BASELINE,lw=.8); ax.axvline(0,color=BASELINE,lw=.8)
ax.set_xlabel("Change in performance (z)"); ax.set_ylabel("Change in role (z)")
ax.set_title("When performance changes, role does not",loc="left")
fig.savefig(FIG/"within_player_change.png",dpi=180,bbox_inches="tight"); plt.show()

# Role gap tails.
tail_plot=tail[tail["allocation"]!="mid"]
fig,ax=plt.subplots(figsize=(6.6,3.8))
for label,color in [("high role / low performance",ORANGE),("low role / high performance",BLUE)]:
    sub=tail_plot[tail_plot["allocation"]==label]
    ax.scatter(sub["perf_z"],sub["role_gap"],s=36,c=color,edgecolors=SURFACE,linewidths=.5,label=label)
ax.axhline(0,color=BASELINE,lw=.8); ax.axvline(0,color=BASELINE,lw=.8)
ax.set_xlabel("Performance (z)"); ax.set_ylabel("Role gap"); ax.legend(frameon=False,fontsize=7)
ax.set_title("Role is not allocated to measured performance",loc="left")
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
# Salary figure 1: star share is flat; rookie volume vs homegrown continuity.
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
ax = axes[0]
for season, color in zip(sorted(panel.season.unique()), [BLUE, ORANGE, AQUA]):
    s = panel[panel.season == season]
    ax.scatter(s["star_share"], s["wins_per_100m"], s=22, c=color, alpha=.75,
               edgecolors=SURFACE, linewidths=.4, label=str(season))
coef = np.polyfit(panel["star_share"], panel["wins_per_100m"], 1)
xs = np.linspace(panel["star_share"].min(), panel["star_share"].max(), 50)
ax.plot(xs, np.polyval(coef, xs), color=GRAY, lw=1.2)
ax.set_xlabel("Star / highlight-reel share of cap spending")
ax.set_ylabel("Wins per $100M")
ax.set_title("Star share: flat", loc="left")
ax.grid(alpha=.7); ax.legend(frameon=False, fontsize=7)
ax = axes[1]
ax.scatter(panel["rookie_snap_share"], panel["wins_per_100m"], s=20, c=ORANGE,
           alpha=.75, edgecolors=SURFACE, linewidths=.4, label="Rookie snap share")
ax.scatter(panel["homegrown_snap_share"], panel["wins_per_100m"], s=20, c=BLUE,
           alpha=.65, edgecolors=SURFACE, linewidths=.4, label="Homegrown snap share")
for col, color in [("rookie_snap_share", ORANGE), ("homegrown_snap_share", BLUE)]:
    c = np.polyfit(panel[col], panel["wins_per_100m"], 1)
    xs = np.linspace(panel[col].min(), panel[col].max(), 50)
    ax.plot(xs, np.polyval(c, xs), color=color, lw=1.5)
ax.set_xlabel("Share of team snaps"); ax.set_ylabel("Wins per $100M")
ax.set_title("Rookie volume vs homegrown continuity", loc="left")
ax.grid(alpha=.7); ax.legend(frameon=False, fontsize=7)
fig.suptitle("The dollar data do not show a simple star or youth premium", x=.01, ha="left")
fig.tight_layout(); fig.savefig(FIG/"salary_efficiency.png", dpi=180, bbox_inches="tight"); plt.show()

# Salary figure 2: QB share vs wins per $100M with a quadratic fit.
qdata = panel.dropna(subset=["wins", "qb_share", "log_payroll", "season_c"]).copy()
q = smf.ols("wins ~ qb_share + I(qb_share**2) + log_payroll + C(season_c)",
            data=qdata).fit(cov_type="cluster", cov_kwds={"groups": qdata["team"]})
q2 = [k for k in q.params.index if k.startswith("I(")][0]
fig, ax = plt.subplots(figsize=(6.6, 4))
for season, color in zip(sorted(panel.season.unique()), [BLUE, ORANGE, AQUA]):
    s = panel[panel.season == season]
    ax.scatter(s["qb_share"], s["wins_per_100m"], s=22, c=color, alpha=.75,
               edgecolors=SURFACE, linewidths=.4, label=str(season))
c = np.polyfit(panel["qb_share"], panel["wins_per_100m"], 2)
xs = np.linspace(panel["qb_share"].min(), panel["qb_share"].max(), 80)
ax.plot(xs, np.polyval(c, xs), color=GRAY, lw=1.5)
ax.axvline(-q.params["qb_share"]/(2*q.params[q2]), color=ORANGE, lw=1, linestyle="--")
ax.set_xlabel("QB share of offense+defense cap spending")
ax.set_ylabel("Wins per $100M")
ax.set_title("The perfect-QB premium flattens", loc="left")
ax.grid(alpha=.7); ax.legend(frameon=False, fontsize=7, title="Season")
fig.tight_layout(); fig.savefig(FIG/"qb_premium.png", dpi=180, bbox_inches="tight"); plt.show()

# Top-quartile QB cap share (2025) vs the rest.
d25 = panel[panel.season == 2025].copy()
d25["top_qb"] = d25["cap_qb_share"] >= d25["cap_qb_share"].quantile(.75)
print(d25.groupby("top_qb")[["wins", "point_diff", "wins_per_100m"]].mean().round(2))
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
    nbf.v4.new_markdown_cell(md_salary_intro),
    nbf.v4.new_code_cell(code_salary_data),
    nbf.v4.new_markdown_cell("## Cost-efficiency models and the QB premium"),
    nbf.v4.new_code_cell(code_salary_models),
    nbf.v4.new_markdown_cell("## Salary figures"),
    nbf.v4.new_code_cell(code_salary_figs),
    nbf.v4.new_markdown_cell(md_weekly),
    nbf.v4.new_code_cell(code_weekly),
    nbf.v4.new_markdown_cell(md_salary_appendix),
    nbf.v4.new_markdown_cell(md_appendix),
    nbf.v4.new_markdown_cell(md_repro),
]
OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUT)
print(OUT)
