from pathlib import Path
from telco_churn.dataset import load_data
from telco_churn.pipeline import numeric_features, categorical_features
import json 
import numpy as np
import joblib

source = Path("data/raw/Telco-Customer-Churn.csv")
source_reference = Path("models/reload_reference.json")
reference_json = json.loads(source_reference.read_text())

list_customer = reference_json["customerIDs"]
list_score= reference_json["scores"]

df = load_data(source)

X_sample = df.set_index("customerID").loc[list_customer]

features = categorical_features+ numeric_features

X_sample= X_sample[features]

pipeline = joblib.load("models/pipeline.joblib")

proba = pipeline.predict_proba(X_sample)
indice = list(pipeline.classes_).index(1)

scores = proba[:, indice]

tolerance = 1e-9
same = np.allclose(list_score, scores, atol=tolerance)
max_diff = np.abs(np.array(list_score) - scores).max()

print(f"Tolerance : {tolerance}")
print(f"Max difference : {max_diff}")
print("Reload check:", "OK" if same else "FAILED")

print(X_sample.shape)                         
print(list(X_sample.index) == list_customer)  