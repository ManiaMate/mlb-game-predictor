# Predicting MLB Game Outcomes Using Starting Pitcher Performance and Historical Data

**Tymon Vu** (tvu38@calpoly.edu) and **Ian Wong** (iwong12@calpoly.edu)  
California Polytechnic State University, San Luis Obispo  
December 2025


## Abstract

This paper presents a machine learning approach to predicting Major League Baseball game outcomes using starting pitcher statistics and team identity features. We construct time-shifted pitcher performance metrics from Baseball Savant data to avoid data leakage and train three classifiers—Logistic Regression, Random Forest, and XGBoost—on 4,301 games from the 2025 MLB regular season. Our best model, XGBoost, achieves 57.8% accuracy and 0.603 AUC, outperforming a Vegas odds baseline (54.3% accuracy, 0.591 AUC). These results demonstrate that pitcher-centric features capture predictive signal beyond market consensus.


## 1. Introduction

Predicting the outcome of professional baseball games is a challenging task due to the sport's inherent randomness and the large number of contributing factors. Unlike sports with fewer possessions or higher-scoring outcomes, baseball features substantial game-to-game variance, making even the best teams unlikely to exceed a 60% regular-season win rate. Even Vegas sportsbooks, with access to proprietary data and professional oddsmakers, fail to predict outcomes correctly nearly half the time.

We approach this problem as a binary classification task: predicting whether the home team will win a given game. Our hypothesis centers on the starting pitcher—arguably the most influential player on the field—who controls the rhythm and pace of the game for 5-7 innings. Unlike lineup decisions that fluctuate daily, starting pitcher assignments are announced in advance and their statistics are readily available, making them ideal predictive features.

**Contributions:**
1. A data pipeline for scraping and preprocessing pitcher game logs from Baseball Savant with proper temporal alignment.
2. A feature engineering approach combining cumulative and rolling pitcher statistics to capture both season-long performance and recent form.
3. An empirical comparison of three classifiers against a Vegas odds baseline, with validation on postseason predictions.


## 2. Data Collection and Preprocessing

### 2.1 Data Sources

Our dataset comprises 4,301 completed regular-season games from the 2025 MLB season, sourced from Shane McDonald's sports data repository. Each record includes game metadata (date, teams, final scores), starting pitchers, and betting odds (moneyline, run line, over/under).

Starting pitcher game logs were scraped from Baseball Savant using Selenium, capturing per-start statistics including innings pitched (IP), earned runs (ER), strikeouts (SO), walks (BB), hits (H), and home runs (HR).

### 2.2 Feature Engineering

A critical design goal was preventing data leakage—ensuring the model only uses information available *before* first pitch. We engineered two categories of pitcher features:

**Season Cumulative Statistics** (calculated from all prior starts):
- **ERA** (Earned Run Average): runs allowed per 9 innings—measures run prevention
- **FIP** (Fielding Independent Pitching): ERA adjusted for defense luck
- **WHIP** (Walks + Hits per Inning Pitched): baserunners allowed
- **K/9** (Strikeouts per 9 innings): strikeout ability
- **BB/9** (Walks per 9 innings): control/command
- **HR/9**, **IP per start**: power allowed and durability

**Rolling 3-Game Statistics** (last three starts):
- ERA, WHIP, K/9, BB/9, HR/9, IP

Baseball is a streaky sport, and recent form often diverges from season averages. The rolling window accounts for whether a pitcher is currently "hot" or in a slump. All statistics are time-shifted by one game (using `.shift(1)`) to ensure each prediction uses only previously observed data.

Additionally, we one-hot encoded team identities for both home and away teams, providing the model with implicit team strength indicators.

### 2.3 Train/Test Split

We employed a temporal split to simulate realistic forecasting:
- **Training set:** Games before September 1, 2025
- **Test set:** Games from September 1 onward (187 games)

This design mirrors a deployment scenario where the model predicts late-season outcomes based on patterns learned from earlier games.


## 3. Methods

### 3.1 Models

We evaluated three classifiers of increasing complexity:

**Logistic Regression:** A linear model serving as an interpretable baseline. Regularization via `max_iter=2000` ensured convergence.

**Random Forest:** An ensemble of 400 decision trees (`max_depth=12`, `min_samples_split=20`) to capture non-linear interactions between pitcher matchups.

**XGBoost:** A gradient boosting model (`n_estimators=300`, `max_depth=5`, `learning_rate=0.05`) with subsampling to reduce overfitting.

### 3.2 Vegas Baseline

As a market-efficiency benchmark, we constructed a baseline that predicts the home team wins if their moneyline implies a higher probability than the away team. Vegas odds were converted to implied probabilities using:

$$P_{home} = \begin{cases} \frac{-ML}{-ML + 100} & \text{if } ML < 0 \\ \frac{100}{ML + 100} & \text{if } ML \geq 0 \end{cases}$$

Probabilities were normalized to remove the vigorish (overround) before comparison.

### 3.3 Evaluation Metrics

We report **accuracy** (proportion of correct predictions) and **ROC-AUC** (area under the receiver operating characteristic curve). AUC measures the model's ability to rank games by win probability, independent of threshold selection.


## 4. Results

Table 1 summarizes model performance on the September 2025 test set.

| Model               | Accuracy | AUC   |
|---------------------|----------|-------|
| Logistic Regression | 56.1%    | 0.583 |
| Random Forest       | 54.5%    | 0.582 |
| XGBoost             | **57.8%**| **0.603** |
| Vegas Baseline      | 54.3%    | 0.591 |

**Key Findings:**

1. **XGBoost outperforms all baselines.** With 57.8% accuracy and 0.603 AUC, XGBoost exceeds both the Vegas baseline (54.3%) and the linear model. This suggests non-linear feature interactions provide additional predictive power.

2. **Models beat the market.** The 3.5 percentage point accuracy improvement over Vegas odds indicates that pitcher-specific features capture information not fully priced into betting lines. This is notable given the efficiency of modern sports betting markets.

3. **Postseason validation.** Aggregating per-game predictions into season-long team strength estimates, our model correctly identified 9 of 11 eventual playoff teams (missing only the Rangers and Giants). It also correctly ranked bottom-tier teams—the Rockies, Nationals, and White Sox—as poor performers throughout the season.

4. **Random Forest underperforms.** Despite its capacity for complex interactions, Random Forest achieved the lowest accuracy (54.5%), likely due to overfitting on the training set or suboptimal hyperparameters. Logistic Regression's competitive 56.1% accuracy demonstrates that even simple feature combinations provide meaningful signal.


## 5. Discussion

### 5.1 Why Pitching Works

Starting pitchers control approximately 5-7 innings of a typical game, directly influencing run prevention. Unlike batting (where any player might get hot), starting pitching assignments are known in advance, making them a reliable pre-game predictor. Our results confirm that season-long and recent pitcher form correlate with game outcomes.

### 5.2 Limitations

We present these results with appropriate cautiousness. Sports prediction is inherently difficult—each game is an independent event, and MLB is notoriously streaky. Several factors constrain model performance:

- **Near-random baseline:** At 57.8% accuracy, our best model remains closer to a coin flip than a reliable oracle. Even Vegas, with superior resources, hovers around 54%.
- **Feature scope:** We exclude team offense (OPS, wRC+), bullpen strength, and defensive metrics, which collectively influence roughly half of each game.
- **Home team bias:** The model shows a tendency to favor home teams, likely due to the one-hot team encodings capturing historical home-field advantage.
- **Pitcher sample size:** Early-season games have minimal historical data per pitcher, causing cold-start issues.

### 5.3 Future Work

Promising directions include:
1. **Holistic features:** Incorporating team offense and bullpen ERA.
2. **Betting ROI analysis:** Evaluating profitability against the spread, not just classification accuracy.
3. **Deep learning:** Sequence models (e.g., LSTM) over pitcher game logs to capture form trajectories.


## 6. Conclusion

We demonstrate that machine learning models trained on time-shifted starting pitcher statistics can predict MLB game outcomes with 57.8% accuracy, outperforming Vegas odds-based predictions by 3.5 percentage points. XGBoost achieved the highest performance, correctly identifying 9 of 11 playoff teams and validating the value of non-linear modeling for this task. While our accuracy remains modest—reflecting the inherent unpredictability of baseball—the results confirm that pitcher-centric features contain meaningful signal. Incorporating team offense and bullpen metrics represents the clearest path toward improved performance.


## References

1. Baseball Savant. (2025). *Statcast Search and Player Pages*. https://baseballsavant.mlb.com
2. McDonald, S. (2025). *MLB Schedules and Odds Data*. https://shanemcd.org

---

*Drafting assistance provided by Claude.*

*Code repository: https://github.com/ManiaMate/mlb-game-predictor*

