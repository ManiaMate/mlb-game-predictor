from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pybaseball import playerid_lookup
import pandas as pd
import unidecode
import os 
import re
import time

# Some pitchers for some raeson are broken and need to manually extract their url link
BROKEN_PITCHERS = {"Charlie Morton": "charlie-morton-450203", 
                   "Luis Castillo": "luis-castillo-622491",
                   "Nestor Cortes": "nestor-cortes-641482",
                   "Nick Martinez": "nick-martinez-607259",
                   "Matthew Boyd": "matthew-boyd-571510",
                   "Eduardo Rodriguez": "eduardo-rodriguez-593958",
                   "Thomas Harrington": "thomas-harrington-802419",
                   "Simeon Woods Richardson": "simeon-woods-richardson-680573",
                   "Luis F. Castillo": "luis-f-castillo-622379",
                   "J.T. Ginn": "j-t-ginn-669372",
                   "Luis Garcia": "luis-garcia-472610",
                   "José De León": "jose-de-leon-592254"}


# Get respective gamelog tables
def extract_gamelog_table(tables):
    for df in tables:
        # drop unnamed columns
        df = df.loc[:, ~df.columns.str.contains("Unnamed")]

        # gamelog ALWAYS has 17 columns after cleaning
        if df.shape[1] == 17:
            first_col = df.iloc[:, 0].astype(str)

            if first_col.str.contains(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|2025").any():
                return df.reset_index(drop=True)

    return None

# Use selenium to connect to chrome and extract data
def get_savant_gamelog_selenium(url):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # wait for JS to load the table
    time.sleep(2)

    html = driver.page_source
    driver.quit()

    tables = pd.read_html(html)
    return extract_gamelog_table(tables)  

# Suffixes to disregard in lookup
SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}

def build_savant_url(full_name, season):
    original = full_name.strip()
    parts = original.split()

    clean_parts = [p for p in parts if p.lower().rstrip(".") not in SUFFIXES]

    first_acc = clean_parts[0]     
    last_acc  = clean_parts[-1]      

    # Player look up to find stats on site
    df = playerid_lookup(last_acc, first_acc)
    if df.empty:
        raise ValueError(f"Player not found: {full_name}")

    mlbam = int(df.iloc[0]["key_mlbam"])

    # Build URL slug
    name_ascii = unidecode.unidecode(original).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", name_ascii).strip("-")

    return (
        f"https://baseballsavant.mlb.com/savant-player/"
        f"{slug}-{mlbam}?stats=gamelogs-r-pitching-mlb&season={season}"
    )


def fetch_broken_pitcher_gamelog(pitcher_name, season, output_dir="./data/starters"):
    if pitcher_name not in BROKEN_PITCHERS:
        print(f"[SKIP] {pitcher_name} is not a broken pitcher.")
        return None
    
    safe_name = unidecode.unidecode(pitcher_name)
    safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", safe_name)
    out_path = f"{output_dir}/{safe_name}.csv"

    # --- SAME CHECK YOU WROTE ---
    if os.path.exists(out_path):
        print(f"[SKIP EXISTS] {pitcher_name} already saved → {out_path}")
        return None

    # Build the BaseballSavant URL from the manual slug
    slug = BROKEN_PITCHERS[pitcher_name]
    url = (
        f"https://baseballsavant.mlb.com/savant-player/"
        f"{slug}?stats=gamelogs-r-pitching-mlb&season={season}"
    )

    print(f"[BROKEN] Fetching {pitcher_name} → {url}")

    try:
        df = get_savant_gamelog_selenium(url)
    except Exception as e:
        print(f"[ERROR] Failed Selenium fetch for {pitcher_name}: {e}")
        return None

    # Validate table
    if df is None or df.empty or "Date" not in df.columns:
        print(f"[EMPTY] No gamelog data for {pitcher_name}")
        return None

    # Clean / filter real dates
    date_mask = df["Date"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")
    df = df[date_mask].reset_index(drop=True)

    # Save file
    os.makedirs(output_dir, exist_ok=True)

    # build safe filename
    safe_name = unidecode.unidecode(pitcher_name)
    safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", safe_name)
    out_path = f"{output_dir}/{safe_name}.csv"

    df.to_csv(out_path, index=False)
    print(f"[SAVED] {pitcher_name} → {out_path}")

    time.sleep(1)
    return df


if __name__ == "__main__":
    for pitcher in BROKEN_PITCHERS:
        fetch_broken_pitcher_gamelog(pitcher, season=2025)
        
    # df = pd.read_csv("./eda/mlb-2025.csv")
    # unique_pitchers = (
    #     df[["Away Starter", "Home Starter"]]
    #     .stack()
    #     .unique()
    #     .tolist()
    # )
    # os.makedirs("./data/starters", exist_ok=True)

    # for pitcher in unique_pitchers:
    #     # build safe filename (same logic as saving)
    #     safe_name = unidecode.unidecode(pitcher)
    #     safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", safe_name)
    #     filepath = f"./data/starters/{safe_name}.csv"

    #     # SKIP if file already exists
    #     if os.path.exists(filepath):
    #         print("Skipping (already exists):", pitcher)
    #         continue

    #     try:
    #         time.sleep(2)
    #         url = build_savant_url(pitcher, 2025)
    #         print(pitcher, ":", url)
    #     except Exception as e:
    #         print("Failed:", pitcher, "|", e)
    #         continue

    #     # scrape
    #     df = get_savant_gamelog_selenium(url)

    #     if df is None or df.empty or "Date" not in df.columns:
    #         print("Skipping:", pitcher, "(no good gamelog)")
    #         continue

    #     # filter dates
    #     date_mask = df["Date"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")
    #     df = df[date_mask].reset_index(drop=True)

    #     # save
    #     df.to_csv(filepath, index=False)
    #     print("Saved:", filepath)