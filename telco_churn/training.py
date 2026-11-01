from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from pathlib import Path
from telco_churn.pipeline import build_pipeline, numeric_features,categorical_features
from telco_churn.evaluation import evaluate_model
from telco_churn.dataset import load_data, split_data
import time
import json






def main() : 
    source = Path("data/raw/Telco-Customer-Churn.csv")

    df = load_data(source)
    train_df ,valid_df,test_df = split_data(df,seed=42)

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

    for name,model in models.items() :
        candidate = build_pipeline(model)
        start = time.perf_counter()
        candidate.fit(X_train,y_train)
        end = time.perf_counter()
        diff = end -start

        metrics = evaluate_model(candidate,X_valid,y_valid)

        result.append(
            {"model" : name, **metrics,
            "params" : model.get_params() , 
            "train_time" : round(diff,4)})

    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2))
    print(result)

if __name__ == "__main__" :
    main()
