from pathlib import Path
from importlib.metadata import version
import hashlib
import json
import sys


import pandas as pd


source = Path("data/raw/Telco-Customer-Churn.csv")
output = Path("reports/data_overview.json")

source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

df = pd.read_csv(source)
raw = pd.read_csv(source, dtype=str, keep_default_na=False)




report = {
    #Data Shape and Types
    "shape" : {"rows" : df.shape[0],"columns": df.shape[1]},
    "datatypes": {c : str(t) for c,t in df.dtypes.items()},

    #Target Count and Proportion
    "target_counts": df["Churn"].value_counts(dropna=False).to_dict(),
    "target_proportions": df["Churn"].value_counts(dropna=False,normalize=True).to_dict(),

    #Duplicate customer-ID count
    "duplicates_customerID" : int(df["customerID"].duplicated().sum()),

    #Missing-value counts, with an explicit check for empty or whitespace-only values.
    "missing_nan" : {c: int(t) for c,t in df.isna().sum().items()},
    "missing_empty": {c: int((raw[c]== "").sum()) for c in raw.columns},
    "missing_whitespace_only": {c: int((raw[c].str.strip().eq("") & raw[c].ne("")).sum()) for c in raw.columns},

    #Source identity/hash and the environment information needed to interpret the run.
    "source" : str(source),
    "source_sha256" : str(source_hash),
    "python_version" : sys.version,
    "pandas_version" : version("pandas")


}

output.parent.mkdir(exist_ok=True,parents=True)
output.write_text(json.dumps(report,indent=2))
print(f"Rapport enregistré dans {output}")



