import joblib
from telco_churn.pipeline import numeric_features,categorical_features


def predict_test(new_customers) :
    required = numeric_features + categorical_features
    missing = [c for c in required if c not in new_customers.columns ]
    if missing : 
        raise ValueError(f"Missing required column {missing}")
        
    loaded_pipeline = joblib.load("models/pipeline.joblib")
    predictions = loaded_pipeline.predict(new_customers)

    return predictions 