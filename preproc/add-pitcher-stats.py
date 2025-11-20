import pandas as pd
import numpy as np
import os
import re
import unidecode

# Convert IPs to Outs
def ip_to_outs(ip):
    if pd.isna(ip):
        return 0
    full = int(ip)
    frac = round((ip - full) * 10)  # .0/.1/.2 -> 0/1/2 outs
    return full * 3 + frac

# Take one pitcher's stats and then 
def apply_one_pitcher_with_statcast(df, pitcher_name, gamelog_csv):
    if not os.path.exists(gamelog_csv):
        print(f"No gamelog CSV for {pitcher_name}: {gamelog_csv}")
        return df

    g = pd.read_csv(gamelog_csv)

    if "Date" not in g.columns:
        print(f"No 'Date' column in {gamelog_csv}")
        return df

    # Calc all cumulitive stats at that point
    g["Date"] = pd.to_datetime(g["Date"])
    g = g.sort_values("Date").reset_index(drop=True)

    g["outs"] = g["IP"].apply(ip_to_outs)
    g["IP_game"] = g["outs"] / 3.0

    g["cum_outs"] = g["outs"].cumsum()
    g["cum_ip"] = g["cum_outs"] / 3.0

    g["cum_ER"] = g["ER"].cumsum()
    g["cum_SO"] = g["SO"].cumsum()
    g["cum_BB"] = g["BB"].cumsum()
    g["cum_HR"] = g["HR"].cumsum()
    g["cum_H"]  = g["H"].cumsum()
    g["cum_GS"] = g["GS"].cumsum()

    ip_cum = g["cum_ip"].replace(0, np.nan)

    g["ERA_cum"]  = 9 * g["cum_ER"] / ip_cum
    g["K9_cum"]   = 9 * g["cum_SO"] / ip_cum
    g["BB9_cum"]  = 9 * g["cum_BB"] / ip_cum
    g["HR9_cum"]  = 9 * g["cum_HR"] / ip_cum
    g["WHIP_cum"] = (g["cum_H"] + g["cum_BB"]) / ip_cum

    FIP_CONST = 3.1
    g["FIP_cum"] = ((13 * g["cum_HR"] + 3 * g["cum_BB"] - 2 * g["cum_SO"]) / ip_cum) + FIP_CONST

    g["IP_per_start_cum"] = g["cum_ip"] / g["cum_GS"].replace(0, np.nan)

    # Rolling last 3 stats - really important because baseball is such a streaky sport
    g["ER_last3"]   = g["ER"].rolling(3).sum()
    g["SO_last3"]   = g["SO"].rolling(3).sum()
    g["BB_last3"]   = g["BB"].rolling(3).sum()
    g["HR_last3"]   = g["HR"].rolling(3).sum()
    g["H_last3"]    = g["H"].rolling(3).sum()
    g["outs_last3"] = g["outs"].rolling(3).sum()
    g["IP_last3"]   = g["outs_last3"] / 3.0

    ip3 = g["IP_last3"].replace(0, np.nan)

    g["ERA_last3"]  = 9 * g["ER_last3"] / ip3
    g["K9_last3"]   = 9 * g["SO_last3"] / ip3
    g["BB9_last3"]  = 9 * g["BB_last3"] / ip3
    g["HR9_last3"]  = 9 * g["HR_last3"] / ip3
    g["WHIP_last3"] = (g["H_last3"] + g["BB_last3"]) / ip3


    season_stat_map = {
        "ERA": "ERA_cum",
        "FIP": "FIP_cum",
        "WHIP": "WHIP_cum",
        "K9": "K9_cum",
        "BB9": "BB9_cum",
        "HR9": "HR9_cum",
        "IP_per_start": "IP_per_start_cum",
    }

    rolling3_stat_map = {
        "ERA_last3": "ERA_last3",
        "WHIP_last3": "WHIP_last3",
        "K9_last3": "K9_last3",
        "BB9_last3": "BB9_last3",
        "HR9_last3": "HR9_last3",
        "IP_last3": "IP_last3",
    }

    for base, col in season_stat_map.items():
        g[base + "_before"] = g[col].shift(1)

    for base, col in rolling3_stat_map.items():
        g[base + "_before"] = g[col].shift(1)

    # first game(s): fill with 0s because full season reset
    before_cols = [k + "_before" for k in season_stat_map.keys()] + \
                  [k + "_before" for k in rolling3_stat_map.keys()]
    g[before_cols] = g[before_cols].fillna(0.0)

    # Add fellow data to respective dates and columns
    g["Date_Start"] = g["Date"].dt.normalize()
    g = g.set_index("Date_Start")

    df["Date_Start_dt"] = pd.to_datetime(df["Date_Start"]).dt.normalize()

    home_mask = df["Home Starter"] == pitcher_name
    away_mask = df["Away Starter"] == pitcher_name

    if not (home_mask.any() or away_mask.any()):
        df = df.drop(columns=["Date_Start_dt"])
        return df

    for base in season_stat_map.keys():
        src_col = base + "_before"
        home_dates = df.loc[home_mask, "Date_Start_dt"]
        away_dates = df.loc[away_mask, "Date_Start_dt"]

        df.loc[home_mask, f"Home_{base}_before"] = home_dates.map(g[src_col])
        df.loc[away_mask, f"Away_{base}_before"] = away_dates.map(g[src_col])

    for base in rolling3_stat_map.keys():
        src_col = base + "_before"
        home_dates = df.loc[home_mask, "Date_Start_dt"]
        away_dates = df.loc[away_mask, "Date_Start_dt"]

        df.loc[home_mask, f"Home_{base}_before"] = home_dates.map(g[src_col])
        df.loc[away_mask, f"Away_{base}_before"] = away_dates.map(g[src_col])

    df = df.drop(columns=["Date_Start_dt"])
    return df

if __name__ == "__main__":
    df = pd.read_csv("./eda/mlb-2025.csv")

    df["Date_Start"] = pd.to_datetime(df["Date_Start"])

    # only keep real games
    df = df[df["Status"] == "Final"]

    # drop duplicate games if any
    df = df.drop_duplicates(subset=["Date_Start", "Away", "Home"], keep="first")

    base_stats = ["ERA", "FIP", "WHIP", "K9", "BB9", "HR9", "IP_per_start"]
    for base in base_stats:
        for side in ["Home", "Away"]:
            col = f"{side}_{base}_before"
            if col not in df.columns:
                df[col] = np.nan

    all_starters = pd.concat([df["Home Starter"], df["Away Starter"]]).dropna().unique()

    # loop over each starter, find their gamelog CSV, and apply
    starters_dir = "./data/starters"
    os.makedirs(starters_dir, exist_ok=True)

    for pitcher_name in all_starters:
        # build safe filename to match how you saved them
        safe_name = unidecode.unidecode(pitcher_name)
        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", safe_name)
        gamelog_csv = os.path.join(starters_dir, f"{safe_name}.csv")

        print(f"\nProcessing {pitcher_name} → {gamelog_csv}")

        df = apply_one_pitcher_with_statcast(
            df,
            pitcher_name=pitcher_name,
            gamelog_csv=gamelog_csv,
        )

    # final output
    df["Home_Win"] = (df["Home Score"] > df["Away Score"]).astype(int)
    df.to_csv("mlb-2025-with-starter-stats.csv", index=False)
    print("\nSaved: mlb-2025-with-starter-stats.csv")
