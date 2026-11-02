from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from pathlib import Path
from importlib.metadata import version
from telco_churn.pipeline import build_pipeline, numeric_features,categorical_features
from telco_churn.evaluation import evaluate_model
from telco_churn.dataset import load_data, split_data
import time
import json
import joblib
import hashlib
import sys






def main() : 
    source = Path("data/raw/Telco-Customer-Churn.csv")
    seed =42

    df = load_data(source)
    train_df ,valid_df,test_df = split_data(df,seed=seed)

    feature_cols = numeric_features + categorical_features

    X_train = train_df[feature_cols]
    y_train = train_df["Churn"].map({"No": 0, "Yes": 1})
    X_valid = valid_df[feature_cols]
    y_valid = valid_df["Churn"].map({"No": 0, "Yes": 1})

    models = {
        "LogisticRegression" : LogisticRegression(max_iter=1000),
        "RandomForestClassifier" : RandomForestClassifier(n_estimators=100,random_state=42,max_depth=8),
        "DecisionTreeClassifier" : DecisionTreeClassifier(random_state=42,max_depth=5),
        "DummyClassifier" :DummyClassifier(strategy="most_frequent")
        }

    result = []
    output = Path("reports/train.json")
    pipeline_record = {}
    

    for name,model in models.items() :
        candidate = build_pipeline(model)
        start = time.perf_counter()
        candidate.fit(X_train,y_train)
        pipeline_record[name] = candidate

        end = time.perf_counter()
        diff = end -start

        metrics = evaluate_model(candidate,X_valid,y_valid)

        
        result.append(
            {"model" : name, **metrics,
            "params" : model.get_params() , 
            "train_time" : round(diff,4)})

    candidates = [f for f in result if f["model"] != "DummyClassifier" ]

    best = max(candidates, key=lambda r: r["avg_precision"])
    
    nom = best["model"]
    print("Selected:", nom)  

    metadata = {
                    "source_hash" : str(hashlib.sha256(source.read_bytes()).hexdigest()),
                    "positive_class_definition" : "1 : Churn (Yes)",
                    "split_seed" : seed,
                    "feature_roles" : {"numeric" : numeric_features , "categorical" : categorical_features} ,
                    "metrics" : best ,
                    "threshold" : 0.5,
                    "customer_allocations" :{"train" : train_df["customerID"].tolist(),"valid" : valid_df["customerID"].tolist(),"test" : test_df["customerID"].tolist()} ,
                    "preprocessing_settings" : {
                        "total_charges_parsing": "whitespace-only values set to missing; other non-numeric text raises an error",
                        "numeric": {"imputer": "median", "scaler": "StandardScaler"},
                        "categorical": {"imputer": "most_frequent", "encoder": "OneHotEncoder(handle_unknown='ignore')"},
                        },
                    "environment": {
                        "python": sys.version,
                        "scikit-learn": version("scikit-learn"),
                        "pandas": version("pandas"),
},
                    
                    
                }


    pipeline_retenu = pipeline_record[nom]
    pipeline_path = Path("models/pipeline.joblib")

    pipeline_path.parent.mkdir(parents=True,exist_ok=True)

    joblib.dump(pipeline_retenu,pipeline_path)

    X_sample = X_valid.head(20)
    X_ids = valid_df.loc[X_sample.index, "customerID"]

    proba_pipeline = pipeline_retenu.predict_proba(X_sample)

    indice = list(pipeline_retenu.classes_).index(1)
    scores = proba_pipeline[:, indice]

    reference = {
        "customerIDs" : X_ids.tolist(),
        "scores" : scores.tolist()
    }

    reference_path = Path("models/reload_reference.json")
    reference_path.write_text(json.dumps(reference,indent=2))

    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2))

    metadata_path = Path("models/pipeline_metadata.json")

    metadata_path.write_text(json.dumps(metadata,indent=2))
    
    

if __name__ == "__main__" :
    main()
