import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def load_data(path) :
    df = pd.read_csv(path)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip().replace("", np.nan), errors="raise")

    return df 

def split_data(df,seed=42) :

    train_df, remaining_df = train_test_split(
    df, test_size=0.4, stratify=df["Churn"], random_state=seed
        )
    valid_df, test_df = train_test_split(
        remaining_df,stratify=remaining_df["Churn"],test_size=0.5,random_state=42
        )

    return train_df, valid_df, test_df

    

    


