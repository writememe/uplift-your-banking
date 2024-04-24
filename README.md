# UP lift your banking


A Python toolkit to manage your budgeting and tracking of your Up Bank accounts.

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

An [examples_folder](examples/) has been provided with some examples. We recommend running either the [untagged_withdrawals](./examples/untagged_withdrawals.py) or the [all_tag_account_analysis](./examples/all_tag_account_analysis.py) example files.

