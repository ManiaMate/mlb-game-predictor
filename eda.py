import pandas as pd

if __name__ == '__main__':
    # Data Preprocessing and cleaning
    df = pd.read_excel('./data/mlb-2025-asplayed.xlsx', sheet_name= "As-Played Schedule")

    df['Save'] = df['Save'].fillna('No Save')

    # Combine the Date and Start Time (EDT) columns into a single datetime
    df['Date_Start'] = pd.to_datetime(
        df['Date'].astype(str) + ' ' + df['Start Time (EDT)'],
        errors='coerce'
    )

    df2 = pd.read_excel('./data/mlb-odds.xlsx', sheet_name= "Betting Odds")

    # Combine the Date and Start Time (EDT) columns into a single datetime
    df2['Date_Start'] = pd.to_datetime(
        df['Date'].astype(str) + ' ' + df['Start Time (EDT)'],
        errors='coerce'
    )

    merged = pd.merge(
        df,
        df2[["Date_Start", "O/U", "Over", "Under", "Away ML", "Home ML", "Home RL Spread", "RL Away", "RL Home"]],
        on="Date_Start",
        how='left'
    )

    merged = merged.drop(columns=['Date'], errors='ignore')
    # Set Date_Start as the main index
    cols = ['Date_Start'] + [col for col in merged.columns if col != 'Date_Start']
    merged = merged[cols]

    merged.to_csv("mlb-2025.csv", index=False)

