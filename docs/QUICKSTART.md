# RollerCoin Quickstart

## Requirements

- Python 3.10+
- A bearer token provided by env var or local token file

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Option A: token file

```bash
cp token.txt.example token.txt
python3 bot_allinone_v2.py
```

## Option B: environment variable

```bash
export ROLLERCOIN_BEARER_TOKEN="replace-me"
python3 bot_allinone_v2.py
```

## Optional config bootstrap

```bash
cp config.example.json config.json
```

## Public-safe note

The public repo excludes real bearer tokens, account-specific logs, and the original per-account runtime folders from the private deployment.
