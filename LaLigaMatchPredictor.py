from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, accuracy_score
import pandas as pd

matches = pd.read_csv("matches.csv", index_col=0)
matches["date"] = pd.to_datetime(matches["date"])
matches["venue_code"] = matches["venue"].astype("category").cat.codes
matches["opp_code"] = matches["opponent"].astype("category").cat.codes
matches["hour"] = matches["time"].str.replace(
    ":.+", "", regex=True).astype("int")
matches["day_code"] = matches["date"].dt.dayofweek
matches["target"] = (matches["result"] == "W").astype("int")

rf = RandomForestClassifier(
    n_estimators=100, min_samples_split=10, random_state=1)

train = matches[matches["date"] < '2024-01-01']
test = matches[matches["date"] > '2024-01-01']
predictors = ["venue_code", "opp_code", "hour", "day_code"]

rf.fit(train[predictors], train["target"])

preds = rf.predict(test[predictors])

# Calculate precision and accuracy
precision = precision_score(test["target"], preds)
accuracy = accuracy_score(test["target"], preds)

combined = pd.DataFrame(dict(actual=test["target"], prediction=preds))
pd.crosstab(index=combined["actual"], columns=combined["prediction"])

print(f"Precision: {precision * 100:.2f}%")
print(f"Accuracy: {accuracy * 100:.2f}%")

grouped_matches = matches.groupby("team")
group = grouped_matches.get_group("Barcelona").sort_values("date")


def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group


cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]
rolling_averages(group, cols, new_cols)
matches_rolling = matches.groupby("team").apply(
    lambda x: rolling_averages(x, cols, new_cols))
matches_rolling = matches_rolling.droplevel('team')
matches_rolling.index = range(matches_rolling.shape[0])
matches_rolling


def make_predictions(data, predictors):
    train = data[data["date"] < '2024-01-01']
    test = data[data["date"] > '2024-01-01']
    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(
        dict(actual=test["target"], prediction=preds), index=test.index)
    precision = precision_score(test["target"], preds)
    return combined, precision


combined, precision = make_predictions(matches_rolling, predictors + new_cols)
precision
combined
combined = combined.merge(matches_rolling[[
                          "date", "team", "opponent", "result"]], left_index=True, right_index=True)
combined


class MissingDict(dict):
    def __missing__(self, key): return key


map_values = {
    "Real Madrid": "Real MA",
    "Atletico Madrid": "Atletico",
    "Athletic Club": "Athletic",
    "Real Sociedad": "Sociedad",
    "Real Betis": "Betis",
    "Celta Vigo": "Celta",
    "Las Palmas": "Palmas",
    "Rayo Vallecano": "Rayo"
}
mapping = MissingDict(**map_values)
combined["new_team"] = combined["team"].map(mapping)
combined
merged = combined.merge(
    combined, left_on=["date", "new_team"], right_on=["date", "opponent"])
merged

print(f"Precision: {precision * 100:.2f}%")
print(f"Accuracy: {accuracy * 100:.2f}%")

