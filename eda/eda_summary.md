# Reflection & Interpretation
### Tymon Vu (tvu38@calpoly.edu) and Ian Wong (iwong12@calpoly.edu)

## Dataset Selection
Data files live [here](../data/), and were sourced from [Shane McDonald's Computer Solution Repository](https://shanemcd.org/).

Our dataset uses the full set of 2025 regular-season games and includes complete, finalized box score statistics for every matchup. This gives us access not only to final scores, but also to team-level performance metrics, pitching and batting summaries, and contextual information such as home/away designation and betting odds. By working with finalized outcomes rather than live or partial data, we ensure consistency across all observations and a reliable foundation for both descriptive analysis and predictive modeling.

- source, structure, relevance
- What is this dataset and why did we choose it?

## Exploratory Data Analysis (EDA)
For the key varaibles we decided to look at, we decided to visualize the given MLB team's betting odds as well as the overall game stats in each game in 2025. Below is a list of all the relevant variables that we will be analyze in order to visualize/see if there are any trends or any relevant signal to predict the game winners. 

Taken from source: 
- `Date_Start`: the date / time of the game
- `Away`: the name of the away team
- `Away Score`: the away team’s score if the game has been played, otherwise this field is empty
- `Home`: the name of the home team
- `Home Score`: the home team’s score if the game has been played, otherwise this field is empty
- `Away Starter`: the starting pitcher of the away team
- `Home Starter`: the starting pitcher of the home team
- `O/U`: the number of runs for an over/under bet
- `Over`: the odds that the Over bet pays, in American odds (AKA moneyline odds) format
- `Under`: the odds that the Under bet pays
- `Away ML`: the odds that the Moneyline bet on the Away team pays
- `Home ML`: the odds that the Moneyline bet on the Home team pays
- `Home RL Spread`: the spread for the Home team on the Run Line bet
- `RL Away`: the odds that the Run Line bet on the Away team pays
- `RL Home`: the odds that the Run Line bet on the Home team pays

Our dataset has exactly 4,301 registered games (rows) of the regular season in the 2025 MLB season. From our EDA, we noticed a couple of things. From the betting odds as visualized in the charts below, the best team as seen, the Los Angeles Dodgers, have an average Moneyline win rate of -125. TThis means that sportsbooks consistently viewed the Dodgers as strong favorites, requiring bettors to wager $125 to profit $100 on average across the season. However, this moneyline number does not seem as drastic as what a "blowout" team would usually have. This signals that the 2025 MLB season has been relatively comopetitive and there weren't raelly any real underdogs in the regular season (besides the Colorodo Rockies).

Additionally, it seems that when comparing sports books original O/U on runs scored on the actual final result of the game, the spots books were mainly accurate. At least if the line was from 6-9 runs, there seems to be a general straight line that matched up that showed how close the final game score is. However, for high scoring games predicted that were above like 10+ runs, the betting lines were raelly off, by either being a really high schoring game or a low scoring game, which makes sense because with such a high number it's unpredictable what could happen.

We also recognize that most teams seem to win a lot more games at home rather than away (at least 50%+). This makes a lot of sense intuitively since teams usually travel the night or day before having to play a baseball game in a region they are unfamiliar with, so there are several of those factors including travel fatigue that could affect a team's performance. 

![Average ML for Wins by Team](imgs/avg_winner_ml.png)
![Runs vs. O/U](imgs/runs_ou.png)
![Wins by Team](imgs/wins_by_team.png)

## Looking Ahead
- Initial ideas for features and any anticipated challenges (imbalance, sparcity, etc.)
- What issues or open questions remain?