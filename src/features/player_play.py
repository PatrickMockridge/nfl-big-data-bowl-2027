"""DL regular-season get-off outcomes.

``player_get_off`` is the time from snap until a pass rusher crosses the line
of scrimmage. We orient it as speed (``-get_off``), remove game/role context
with a cross-fitted model, and aggregate the residuals to players with
empirical-Bayes shrinkage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data import load

DL_POSITIONS = {"DE", "DT", "NT", "OLB"}

NUMERIC_CONTEXT = [
    "yards_to_go",
    "yardline_number",
    "pass_length",
    "score_margin",
    "expected_points",
    "game_clock_seconds",
    "week",
    "quarter",
]

CATEGORICAL_CONTEXT = [
    "nfl_position",
    "down",
    "team_coverage_man_zone",
    "team_coverage_type",
    "pass_result",
    "play_direction",
    "season",
]
# Team identity is deliberately excluded: players are nested in teams, so a
# team fixed effect absorbs player quality. Scheme/coverage/role controls remain.


def game_seconds(value: str) -> float:
    try:
        minutes, seconds = str(value).split(":")
        return int(minutes) * 60 + int(seconds)
    except (ValueError, AttributeError):
        return np.nan


def dl_plays(rookie_only: bool = True, season_type: str | None = "REG") -> pd.DataFrame:
    players = load.load_players()
    ids = set(players.loc[players["nfl_position"].isin(DL_POSITIONS), "nfl_id"])
    pp = load.load_player_play(
        usecols=[
            "game_id",
            "play_id",
            "team_abbr",
            "nfl_id",
            "lined_up_position",
            "down",
            "yards_to_go",
            "quarter",
            "yardline_number",
            "game_clock",
            "pre_snap_home_score",
            "pre_snap_visitor_score",
            "play_direction",
            "expected_points",
            "pass_result",
            "pass_length",
            "team_coverage_man_zone",
            "team_coverage_type",
            "player_get_off",
            "blitzing",
        ]
    )
    pp = pp[pp["nfl_id"].isin(ids)].copy()
    pp = pp[pp["player_get_off"].notna()].copy()
    pp["nfl_position"] = pp["nfl_id"].map(
        players.set_index("nfl_id")["nfl_position"]
    )
    pp["draft_year"] = pp["nfl_id"].map(
        players.set_index("nfl_id")["draft_year"]
    )
    pp["score_margin"] = pp["pre_snap_home_score"] - pp["pre_snap_visitor_score"]
    pp["game_clock_seconds"] = pp["game_clock"].map(game_seconds)
    games = load.load_games()[["game_id", "season", "week", "season_type"]]
    pp = pp.merge(games, on="game_id", how="left")
    pp["season"] = pp["season"].astype("Int64")
    pp["verified_speed"] = -pp["player_get_off"]
    if season_type is not None:
        pp = pp[pp["season_type"] == season_type].copy()
    if rookie_only:
        pp = pp[pp["season"] == pp["draft_year"]].copy()
    return pp


def _model(categorical_context: list[str] | None = None) -> Pipeline:
    cats = CATEGORICAL_CONTEXT if categorical_context is None else categorical_context
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            ),
        ]
    )
    pre = ColumnTransformer(
        [
            ("num", numeric, NUMERIC_CONTEXT),
            ("cat", categorical, cats),
        ],
        sparse_threshold=1.0,
    )
    return Pipeline([("pre", pre), ("ridge", Ridge(alpha=1.0))])


def cross_fitted_residuals(
    plays: pd.DataFrame,
    n_splits: int = 5,
    categorical_context: list[str] | None = None,
) -> pd.Series:
    """Residuals from a context model that never sees the player's own plays."""
    cats = CATEGORICAL_CONTEXT if categorical_context is None else categorical_context
    X = plays[NUMERIC_CONTEXT + cats]
    y = plays["verified_speed"].to_numpy()
    groups = plays["nfl_id"].to_numpy()
    residuals = np.full(len(plays), np.nan)
    gkf = GroupKFold(n_splits=n_splits)
    for train_idx, test_idx in gkf.split(X, y, groups=groups):
        model = _model(cats)
        model.fit(X.iloc[train_idx], y[train_idx])
        residuals[test_idx] = y[test_idx] - model.predict(X.iloc[test_idx])
    return pd.Series(residuals, index=plays.index, name="context_residual")


def out_of_time_residuals(
    plays: pd.DataFrame,
    train_years: tuple[int, int] = (2023, 2024),
    test_year: int = 2025,
    categorical_context: list[str] | None = None,
) -> pd.Series:
    """Train context on earlier draft classes, predict the held-out class."""
    cats = CATEGORICAL_CONTEXT if categorical_context is None else categorical_context
    train = plays["draft_year"].isin(train_years)
    test = plays["draft_year"] == test_year
    X = plays[NUMERIC_CONTEXT + cats]
    y = plays["verified_speed"].to_numpy()
    residuals = np.full(len(plays), np.nan)
    model = _model(cats)
    model.fit(X.loc[train], y[train.to_numpy()])
    residuals[test.to_numpy()] = y[test.to_numpy()] - model.predict(X.loc[test])
    # Cross-fit the training years so every player has an out-of-player residual.
    train_plays = plays.loc[train].copy()
    train_plays["context_residual"] = cross_fitted_residuals(
        train_plays, categorical_context=cats
    )
    residuals[train.to_numpy()] = train_plays["context_residual"].to_numpy()
    return pd.Series(residuals, index=plays.index, name="context_residual")


def empirical_bayes(
    df: pd.DataFrame, value: str = "context_residual"
) -> pd.DataFrame:
    """Shrink player means toward zero using between/within variance."""
    grouped = df.groupby("nfl_id")[value]
    stats = grouped.agg(["mean", "count", "var"]).reset_index()
    stats = stats.rename(
        columns={"mean": "raw_mean", "count": "n_plays", "var": "within_var"}
    )
    stats["within_var"] = stats["within_var"].fillna(0.0)
    within_noise = stats["within_var"] / stats["n_plays"]
    between_var = stats["raw_mean"].var(ddof=0)
    tau2 = max(float(between_var - within_noise.mean()), 0.0)
    if tau2 == 0:
        stats["shrunk_mean"] = 0.0
    else:
        stats["shrunk_mean"] = (
            stats["raw_mean"] * tau2 / (tau2 + within_noise)
        )
    stats["tau2"] = tau2
    return stats


def player_outcomes(plays: pd.DataFrame) -> pd.DataFrame:
    players = load.load_players()
    out = empirical_bayes(plays)
    raw = (
        plays.groupby("nfl_id")["verified_speed"]
        .agg(raw_speed_mean="mean", raw_speed_count="count")
        .reset_index()
    )
    out = out.merge(raw, on="nfl_id", how="left")
    out["draft_year"] = out["nfl_id"].map(
        players.set_index("nfl_id")["draft_year"]
    )
    out["nfl_position"] = out["nfl_id"].map(
        players.set_index("nfl_id")["nfl_position"]
    )
    rookie_team = (
        plays.groupby(["nfl_id", "team_abbr"]).size().reset_index(name="n")
        .sort_values(["nfl_id", "n"])
        .drop_duplicates("nfl_id", keep="last")
        .set_index("nfl_id")["team_abbr"]
    )
    out["rookie_team"] = out["nfl_id"].map(rookie_team)
    return out


def player_season_outcomes(plays: pd.DataFrame) -> pd.DataFrame:
    """Empirical-Bayes player-season means from context residuals."""
    out = (
        plays.groupby(["nfl_id", "season"])
        .agg(
            raw_mean=("context_residual", "mean"),
            n_plays=("context_residual", "size"),
            within_var=("context_residual", "var"),
        )
        .reset_index()
    )
    out["within_var"] = out["within_var"].fillna(0.0)
    noise = out["within_var"] / out["n_plays"]
    tau2 = max(float(out["raw_mean"].var(ddof=0) - noise.mean()), 0.0)
    if tau2 > 0:
        out["shrunk_mean"] = out["raw_mean"] * tau2 / (tau2 + noise)
    else:
        out["shrunk_mean"] = 0.0
    out["tau2"] = tau2
    return out


def weekly_residuals(plays: pd.DataFrame) -> pd.DataFrame:
    """Weekly mean context residual per player-season."""
    return (
        plays.groupby(["nfl_id", "season", "week"])
        .agg(
            weekly_mean=("context_residual", "mean"),
            weekly_n=("context_residual", "size"),
        )
        .reset_index()
        .sort_values(["nfl_id", "season", "week"])
    )


def flip_dwell(weekly: pd.DataFrame) -> pd.DataFrame:
    """Temporal Möbius inputs: weekly sign flips and dwell per player-season."""
    rows = []
    for (nfl_id, season), sub in weekly.groupby(["nfl_id", "season"]):
        values = sub["weekly_mean"].to_numpy()
        if len(values) < 2:
            rows.append(
                {
                    "nfl_id": nfl_id,
                    "season": season,
                    "weeks": len(values),
                    "flip_rate": np.nan,
                    "dwell": np.nan,
                    "weekly_sd": np.nan,
                }
            )
            continue
        signs = np.sign(values - values.mean())
        signs = signs[signs != 0]
        flips = np.sum(signs[1:] != signs[:-1]) if len(signs) > 1 else 0
        flip_rate = flips / (len(signs) - 1) if len(signs) > 1 else np.nan
        runs = []
        if len(signs):
            current = signs[0]
            length = 1
            for sign in signs[1:]:
                if sign == current:
                    length += 1
                else:
                    runs.append(length)
                    current = sign
                    length = 1
            runs.append(length)
        rows.append(
            {
                "nfl_id": nfl_id,
                "season": season,
                "weeks": len(values),
                "flip_rate": flip_rate,
                "dwell": float(np.median(runs)) if runs else np.nan,
                "weekly_sd": float(np.std(values, ddof=1)),
            }
        )
    return pd.DataFrame(rows)


def reliability(plays: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # Split-half odd/even within player.
    d = plays.copy()
    d["row"] = d.groupby("nfl_id").cumcount()
    odd = d[d["row"] % 2 == 1].groupby("nfl_id")["context_residual"].mean()
    even = d[d["row"] % 2 == 0].groupby("nfl_id")["context_residual"].mean()
    paired = pd.concat([odd, even], axis=1).dropna()
    raw = spearmanr(paired.iloc[:, 0], paired.iloc[:, 1]).statistic
    rows.append(
        {
            "check": "split_half_odd_even",
            "players": len(paired),
            "rho": raw,
            "spearman_brown": 2 * raw / (1 + raw) if raw > -1 else np.nan,
        }
    )
    # Season-to-season for the 2023 class (rookie vs sophomore).
    season = player_season_outcomes(plays)
    season["draft_year"] = season["nfl_id"].map(
        load.load_players().set_index("nfl_id")["draft_year"]
    )
    d23 = season[(season["draft_year"] == 2023) & (season["season"].isin([2023, 2024]))]
    wide = d23.pivot(index="nfl_id", columns="season", values="raw_mean")
    if {2023, 2024}.issubset(wide.columns):
        paired = wide[[2023, 2024]].dropna()
        rho = spearmanr(paired[2023], paired[2024]).statistic
        rows.append(
            {
                "check": "season_2023_vs_2024",
                "players": len(paired),
                "rho": rho,
                "spearman_brown": 2 * rho / (1 + rho) if rho > -1 else np.nan,
            }
        )
    return pd.DataFrame(rows)
