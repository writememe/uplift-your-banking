[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![yamllint](https://img.shields.io/badge/YAML-linter-yamllint-blue)](https://github.com/adrienverge/yamllint)

# Uplift your banking with Up

A Python toolkit to manage your budgeting and tracking of your [Up Bank accounts](https://up.com.au/).

This is built on the good work of [@jcwillox](https://github.com/jcwillox) who did the hard work with created the [up-bank-api client](https://github.com/jcwillox/up-bank-api)

You can use this toolkit to track your tagged transactions, perform budget variance analysis and perform spend analysis over different time periods.

All reports outputted are in Excel, but given that they are Pandas dataframes, there is nothing stopping the outputs being sent to other file formats.

## Pre-requisites

The following pre-requisites are assumed when using this toolkit:

- Understanding of Python
- Python 3.10 or greater installed
- Ability to read/create CSV and JSON files
- An [Up Bank account], if you don't have one, feel free to create one using [my invite code](https://hook.up.me/dfjt)
- [Poetry installed on your machine](https://python-poetry.org/docs/#installation)
## Setup

The following steps need to be followed:

1) Setup your [personal access token from the Up Developer Documentation](https://developer.up.com.au/#getting-started)
2) Set the personal access token as the `UP_TOKEN` environmental variable

```bash
export UP_TOKEN="<YOUR_TOKEN>"

```
3) Setup Poetry, [which will install the dependencies from the `poetry.lock` file](https://python-poetry.org/docs/basic-usage/#installing-with-poetrylock):

```bash
poetry install
```

## Examples

An [examples_folder](examples/) has been provided with some examples.

The examples are as follows:

| Example Name | Description | Comments |
| ---------- | ------------ | ----------------- | 
| [untagged_withdrawals](./examples/untagged_withdrawals.py)|Find all transactions for an account within a defined period and generate an Excel report with the untagged transactions| |
| [all_tag_account_analysis](./examples/all_tag_account_analysis.py)|Perform a tag analysis for all tag-based transactions for the last three months and save to an Excel file| Relies upon transactions [being tagged](https://developer.up.com.au/#tags) through the app or the API |
| [budget_tracking](./examples/budget_tracking.py)|Perform a budget vs spend analysis for tags, for an account within a defined period and generate an Excel report with the untagged transactions| See the [BUDGET_TRACKER_README](/inputs/README.md) for some help on the formatting of your budget file.|
| [multi_report_workflow](./examples/multi_report_workflow.py)|Perform all three examples above within a single workflow| See the [BUDGET_TRACKER_README](/inputs/README.md) for some help on the formatting of your budget file.|

