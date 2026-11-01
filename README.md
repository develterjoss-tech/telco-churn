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


