# Data source

## Source
- Dataset: IBM Telco Customer Churn
- Repository: https://github.com/IBM/telco-customer-churn-on-icp4d
- Commit-pinned download: https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/1fd6fd70906479be1712e64cfc0ea89f58466629/data/Telco-Customer-Churn.csv

## Local location
- `data/raw/Telco-Customer-Churn.csv` (original, unchanged; `data/` is ignored by Git)

## Identity
- SHA-256: `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`
- Verify: `shasum -a 256 data/raw/Telco-Customer-Churn.csv`
- A different hash means a different file, even if the name is the same. Do not open or re-save the CSV in a spreadsheet application.

## Field notes
| Role | Fields |
|---|---|
| Customer identifier | `customerID` |
| Potential numeric inputs | `tenure`, `MonthlyCharges`, `TotalCharges` |
| Potential categorical inputs | `Contract`, `InternetService`, `PaymentMethod` (and the other service fields) |
| Target | `Churn` (`Yes` / `No`) |

- 7043 rows, 21 columns, one row per customer: a snapshot, not an event history.
- `TotalCharges` contains 11 whitespace-only values (`" "`, customers with `tenure = 0`), so pandas reads it as text.
- The first copy I received (`datasets.csv`) had every line wrapped in quotes and was not the original file. It was replaced by the commit-pinned download above.
