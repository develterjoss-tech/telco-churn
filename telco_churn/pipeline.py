from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np


numeric_features = ["tenure","MonthlyCharges","TotalCharges"]
categorical_features = ["Contract","InternetService","PaymentMethod"]

def build_pipeline(classifier) :
    
    numeric_transformer = Pipeline([
        ("imputer",SimpleImputer(strategy="median")),
        ("scaler",StandardScaler()) 
        ])

    categorical_transformer = Pipeline([
        ("imputer",SimpleImputer(strategy="most_frequent")),
        ("encoder",OneHotEncoder(handle_unknown="ignore")) 
        ])

    preprocessor = ColumnTransformer([
        ("num",numeric_transformer,numeric_features),
        ("cat",categorical_transformer,categorical_features)
        ])

    pipe = Pipeline([
        ("preprocessor",preprocessor),
        ("classifier",classifier)
        ])
    return pipe 
