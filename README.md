# Telco Churn - Reproducible Churn Project

TP01 of the MLOps course (ESILV). Business question: a telecom company wants to predict which customers will churn. Before any model is trained, this project establishes a structure, an environment, a data-source record and an inspection report that a teammate can reproduce without asking me anything.

This is a customer **snapshot** (one row per customer), not a dated event history or a randomized retention experiment: results describe associations, not causes.

## Setup

Requirements: Git, [uv](https://docs.astral.sh/uv/), Python 3.12 (uv installs it if needed).

    git clone https://github.com/develterjoss-tech/telco-churn.git
    cd telco-churn
    uv sync --locked

`--locked` fails if `uv.lock` does not match `pyproject.toml`, instead of silently resolving new versions.

Check that the interpreter and the package import correctly:

    uv run python --version
    uv run python -c "import telco_churn; print(telco_churn.__file__)"

## Source data

The raw CSV is **not** tracked by Git (`data/` is ignored). Download the commit-pinned original from the [IBM Telco repository](https://github.com/IBM/telco-customer-churn-on-icp4d):

    mkdir -p data/raw
    curl -L -o data/raw/Telco-Customer-Churn.csv https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/1fd6fd70906479be1712e64cfc0ea89f58466629/data/Telco-Customer-Churn.csv
    shasum -a 256 data/raw/Telco-Customer-Churn.csv

Expected SHA-256:

    16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91

If your hash differs, you do not have the same file. Do not open or re-save the CSV in a spreadsheet application. Details: `references/data_source.md`.

## Run the inspection

    uv run python scripts/inspect_data.py

This writes `reports/data_overview.json` (dimensions and types, target counts and proportions, duplicate customer IDs, NaN / empty / whitespace-only counts, source SHA-256, Python and pandas versions). The script only inspects: it removes nothing, imputes nothing, splits nothing and trains nothing.

Expected on the original file: 7043 rows, 21 columns, target No 5174 / Yes 1869, 0 duplicate IDs, 11 whitespace-only values in `TotalCharges` (0 NaN, 0 empty).

## Project layout

Generated with Cookiecutter Data Science v2.3.0 (`uvx --from cookiecutter-data-science ccds`). Options: dataset storage none, environment manager uv, dependency file pyproject.toml, pydata packages none, testing none, ruff, no license, docs none, no code scaffold, Python 3.12.

| Path | Purpose |
|---|---|
| `data/raw/` | Original, unchanged CSV (the whole `data/` folder is ignored by Git) |
| `data/interim/`, `data/processed/`, `data/external/` | Created by the template; later: intermediate, prepared and third-party data |
| `telco_churn/` | Importable package (CCDS v2 layout, no `src/`) |
| `scripts/inspect_data.py` | Command-line inspection entry point |
| `reports/data_overview.json` | Generated inspection report (tracked on purpose) |
| `references/data_source.md` | Source, location and hash of the CSV |
| `evidence/tp01/` | Before/after environment recreation evidence |
| `notebooks/` | Exploratory work (empty for now, not the only runnable workflow) |
| `models/` | Later (TP02): fitted pipelines and metadata |
| `Makefile` | Template shortcuts (`make requirements`, `make clean`, `make lint`); not used in TP01, the README runs `uv` directly |
| `docs/` | Template placeholder (only a `.gitkeep`), unused: docs option was set to none |
| `pyproject.toml`, `uv.lock` | Dependencies and exact resolved versions (both tracked) |

`.venv/` (local environment) and `venv.bak/` (backup of the previous one, see below) are ignored by Git. `configs/` and `tests/` will be added in TP02 when needed.

## Environment recreation check

I moved the old environment aside (`mv .venv venv.bak`), recreated it with `uv sync --locked`, and ran the same script on the same CSV in both environments. Result: identical reports, same Python 3.12.13 and package versions, same source hash. `venv.bak/` is local only, a fresh clone does not have it. Evidence and procedure: `evidence/tp01/` (`comparison.txt`, `recreation.md`).

Limit: the lockfile pins package versions, not hardware, operating system or future training details.

## Answers to the TP questions

**Environment and structure**
- `pyproject.toml` declares the project and its dependencies; `uv.lock` records the exact resolved versions (committed, for reproducibility); `.venv/` is the local installed environment (generated, ignored, never copied).
- Notebooks are exploratory and hard to test or import; reusable logic belongs in the package so scripts, tests and later pipelines can share it.
- The fitted model is an output and goes in `models/`; the code that builds it is source code and goes in the package (`telco_churn/`).

**Data identity**
- Two files with the same name can contain different data: the name is only a label, and only the SHA-256 identifies the content. In this project, my first copy (`datasets.csv`) looked like the dataset but every line was wrapped in quotes, so pandas read a single column; the original file has different bytes and a different hash. A file named `Telco-Customer-Churn.csv` that was re-saved in a spreadsheet would likewise keep its name but get another hash.
- A matching hash only proves it is exactly the same file, not that the business data are correct: a file full of errors has a perfectly stable hash.
- The target (`Churn`) must not be an input, otherwise the model sees the answer (leakage). `customerID` is an arbitrary label with no business meaning: the model could memorize customers instead of learning patterns that generalize.

**Inspection**
- `TotalCharges` is read as text because 11 values are a single space (`" "`), which pandas does not treat as missing and cannot convert to a number. `isna()` reports 0 for it; only the whitespace check finds them (they are customers with `tenure = 0`).
- A saved report can be attached as evidence, compared between runs and read by other programs; printed output disappears.
- Always predicting "No" gives about 73.5% accuracy but finds no churner (recall 0), so accuracy alone is not a meaningful baseline in TP02: it must be compared on churn-specific metrics.


**Git**
- A commit identifies a complete snapshot of the repository at one moment (content, author, date, message, parent), referenced by a hash.
- Uncommitted edits are not recorded: nobody else can retrieve or reproduce them, and the last commit no longer matches what is on my disk.
- A helpful PR description says what changes and why, how it was verified, what was not verified, and what the reviewer should look at.

**What can another engineer reproduce now, and what is missing for a trained model?**
- They can recreate the environment from `uv.lock`, identify the input data by its SHA-256 and regenerate the same inspection report.
- To reproduce a trained model we would also need the training configuration, the train/test split and random seeds, the preprocessing pipeline, the metrics, and the saved model with its metadata.

## Handover

The peer handover test was not carried out. Remaining limit: these instructions have not been tested by someone else from a clean clone.

## TP02 - Training pipeline

Goal: train a churn model, compare a few candidates, and save a pipeline that can predict on new customers without retraining.

### How to run

All commands are run from the project root.

    uv sync --locked
    uv run python -m telco_churn.training      # train, compare, save the best pipeline
    uv run python -m telco_churn.check_reload  # reload the saved pipeline in a new process and compare scores
    uv run python -m telco_churn.checks        # reliability checks

Training writes:

- `reports/train.json`: comparison table (4 models, parameters, fit time, metrics)
- `models/pipeline.joblib`: the selected fitted pipeline (preprocessing + classifier)
- `models/pipeline_metadata.json`: source hash, seed, customer IDs of each split, features, preprocessing, threshold, metrics, library versions
- `models/reload_reference.json`: scores of 20 validation customers, used by the reload check

The `.joblib` file is small, so it is committed. It can be rebuilt with the training command. Only load it if you trust it, and use the same scikit-learn version as in the metadata.

### Code layout

| File | Role |
|---|---|
| `telco_churn/dataset.py` | read the CSV, convert `TotalCharges`, split train/validation/test |
| `telco_churn/pipeline.py` | build an unfitted pipeline for any classifier |
| `telco_churn/evaluation.py` | compute the metrics |
| `telco_churn/training.py` | train and compare the models, select one, save it |
| `telco_churn/prediction.py` | load the saved pipeline and predict |
| `telco_churn/check_reload.py`, `checks.py` | proofs that reload and the pipeline behave correctly |

### Task and split

Positive class: `Churn = Yes` (encoded 1). `customerID` and `Churn` are never used as inputs.

The split is stratified 60/20/20 with seed 42: 4225 train, 1409 validation, 1409 test. No customer ID appears in two sets. The test set is not used anywhere in this work.

First model (only `tenure` and `MonthlyCharges`, logistic regression), on validation: accuracy 0.783, confusion matrix [[950, 85], [221, 153]] (rows = true No/Yes, columns = predicted No/Yes). The majority-class baseline gets 0.735 and finds no churner: [[1035, 0], [374, 0]].

### Preprocessing

Inputs: `tenure`, `MonthlyCharges`, `TotalCharges` (numeric) and `Contract`, `InternetService`, `PaymentMethod` (categorical).

- `TotalCharges` is read as text because 11 values are a single space. Before the pipeline, whitespace-only values become missing. Any other text that is not a number raises an error. This is done in `load_data`, so training and prediction use the same rule.
- Numeric: missing values filled with the median, then standardised.
- Categorical: missing values filled with the most frequent value, then one-hot encoded. An unknown category at prediction time is ignored (all zeros).
- Everything is learned on the training set only, inside the pipeline.

### Model comparison and selection

Same six features and same split for every model. Metrics on validation, threshold 0.5.

| Model | Average precision | Precision | Recall | F1 | Accuracy |
|---|---|---|---|---|---|
| Majority baseline | 0.265 | 0.000 | 0.000 | 0.000 | 0.735 |
| Logistic regression | 0.647 | 0.664 | 0.529 | 0.589 | 0.804 |
| Random forest (100 trees, depth 8) | 0.670 | 0.644 | 0.508 | 0.568 | 0.795 |
| Decision tree (depth 5) | 0.603 | 0.630 | 0.602 | 0.616 | 0.801 |

Selection rule: highest average precision on the validation set, baseline excluded. I use average precision because it compares how well each model ranks customers by risk and does not depend on the 0.5 threshold. I looked at the table before writing this, so the choice was not fixed in advance.

Selected: random forest. Its lead over logistic regression is small (0.023). With 374 churners in validation this may be noise, and the simpler logistic regression would also be a reasonable choice.

The first model uses only two features, so it cannot be compared with these models to say one algorithm is better.

### Checks

Output saved in `evidence/tp02/`.

- Reload: scores of 20 customers from the saved pipeline match the original ones (max difference 0.0, tolerance 1e-9). See `reload_check.txt`.
- Customer IDs are disjoint across the three sets.
- The imputer statistics equal the medians of the training set, and calling `predict` does not change them.
- A missing `TotalCharges` is filled with the training median.
- An unknown category is accepted without an error, but the model does not see it, so the prediction is less reliable. One prediction changed in my test.
- A missing required column raises an error that names the column.

### Limits

- The default threshold of 0.5 gives a recall of about 0.5: half of the churners are missed. The threshold can be lowered, but I did not do it here.
- Differences between the three models are small and come from a single validation split.
- `predict_test` returns classes at the model's default threshold, which is 0.5 for a random forest.
- No peer review or handover test was done, for TP01 or TP02. The instructions have only been tested by me.
