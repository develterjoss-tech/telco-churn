import joblib
import numpy as np

from telco_churn.dataset import load_data, split_data
from telco_churn.pipeline import numeric_features, categorical_features
from telco_churn.prediction import predict_test

df = load_data("data/raw/Telco-Customer-Churn.csv")
train_df, valid_df, test_df = split_data(df, seed=42)
pipeline = joblib.load("models/pipeline.joblib")
X = valid_df[numeric_features + categorical_features].head(5)

train_ids, valid_ids, test_ids = (set(d["customerID"]) for d in (train_df, valid_df, test_df))
assert not (train_ids & valid_ids or train_ids & test_ids or valid_ids & test_ids)
print("1. IDs disjoints : OK")

imputer = pipeline.named_steps["preprocessor"].named_transformers_["num"].named_steps["imputer"]
before = imputer.statistics_.copy()
assert np.allclose(before, train_df[numeric_features].median())
print("2. Statistiques = médianes du train : OK")

pipeline.predict(X)
assert np.array_equal(before, imputer.statistics_)
print("3. predict ne modifie pas l'imputer : OK")

X_nan = X.copy()
X_nan.iloc[0, X_nan.columns.get_loc("TotalCharges")] = np.nan
print("4a. TotalCharges manquant :", predict_test(X_nan))
X_new = X.copy()
X_new["Contract"] = "Unseen"
print("4b. Contract inconnu      :", predict_test(X_new))

try:
    predict_test(X.drop(columns=["Contract"]))
    print("5. FAILED : aucune erreur")
except ValueError as error:
    print("5. Erreur levée :", error)