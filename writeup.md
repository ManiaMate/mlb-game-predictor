# MLB Game Predictor
### Tymon Vu (tvu38@calpoly.edu) and Ian Wong (iwong12@calpoly.edu)

## Data Collection & Preprocessing
We began by aggregating game schedules and results with vegas betting odds (`eda/eda.py`). To retrieve data on starting pitching, we built a scraper (`preproc/web-scrape.py`) utilizing Selenium to fetch game logs from Baseball Savant.

We then engineered features in `preproc/add-pitcher-stats.py`. For each game, we calculated the starting pitchers' season-to-date and recent (last 3 games) statistics, including ERA, FIP, WHIP, and K/9. We time-shifted these statistics to ensure the model only sees data available *before* the first pitch, preventing data leakage.

## Baseline Model Training & Evaluation
We are approaching the problem as a binary classification task: predicting whether the Home team will win (`model.py`). Thus far, we've established a baseline using three distinct approaches to set a performance floor.

**Features:**
- **Pitcher Stats:** Season cumulative and rolling (last 3) metrics for both Home and Away starters. This balanced long-term performance (season) with current performance (recent games).
- **Vegas Odds:** Moneyline odds for both teams, which serve as a proxy for market sentiment and implied probability.

**Methodology:**
We utilized a time-based split, training on games before September 1st, 2025, and testing on the final month of the season. This simulates a realistic forecasting scenario. Pitchers will reset with a season total of 0 on all of their stats. Each game will aggregate new data to account for future games. For example, a pitcher that stats his first game will have 0 ERA, 0 K/BB etc., and then in his second game, his ERA and K/BB stats will change to reflect the results after game 1. This ensures that there will be no leakage or influence over future games that will affect our model as a result. 

**Baseline Models:**
1.  **Random Baseline:** A purely random control as a benchmark.
2.  **Logistic Regression:** A linear baseline that captures simple relationships between stats and win probability.
3.  **Random Forest:** A non-linear baseline that captures complex interactions between pitcher matchups and odds.

**Results:**
We evaluated performance using Accuracy and ROC-AUC scores. The Random Forest outperformed the other models in the baseline.
*   **Logistic Regression:** ~54% Accuracy, 0.575 AUC
*   **Random Forest:** ~59% Accuracy, 0.601 AUC
*   **Random:** ~52% Accuracy, 0.517 AUC

## Analysis & Future Work
**Strengths & Weaknesses:**
Our baseline has a decent amount of variety, from random guessing to complex non-linear modeling. The Random Forest (58.5% accuracy) outperforms the linear model because it captures conditional interactions (e.g., a high ERA matters less against a weak opponent) that Logistic Regression misses. However, even this strong baseline ignores offensive and bullpen performance, limiting its ceiling.

**Potential Bias:**
It is possible that both the linear and non-linear baselines over-rely on Vegas odds rather than finding independent signal. This could lead to the models simply copying the market, since it knows it to be efficient.

**Future Directions:**
To beat this strong baseline, we will continue to explore:
1.  **Advanced Algorithms:** Implementing Gradient Boosting (XGBoost) to natively handle missing data and potentially squeeze out more performance than the Random Forest.
2.  **Holistic Features:** Adding team offense (OPS) and bullpen ERA to look beyond just the starting pitcher.
3.  **Betting ROI:** Evaluating success based on profitability against Vegas odds, not just raw accuracy.