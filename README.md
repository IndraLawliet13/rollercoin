# rollercoin

[![CI](https://github.com/IndraLawliet13/rollercoin/actions/workflows/python-smoke.yml/badge.svg)](https://github.com/IndraLawliet13/rollercoin/actions/workflows/python-smoke.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Target](https://img.shields.io/badge/Target-RollerCoin-111827)
![Flow](https://img.shields.io/badge/Flow-Tap%20%7C%20Tasks%20%7C%20Upgrades-7C3AED)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Python automation script for a RollerCoin tap and upgrade workflow with balance checks, task claims, wheel spins, daily reward attempts, energy recharge, miner upgrade heuristics, and local activity logging.

This public candidate is prepared as a safe showcase version of the original working project. The private multi-account deployment folders were collapsed into a single reusable codebase, while live bearer tokens, per-account runtime JSON, and account-specific logs were excluded.

## Overview

`rollercoin` is a supporting-showcase repo centered on one reusable all-in-one bot entry point that handles the common balance, reward, tapping, and miner-purchase cycle.

The public repo keeps the automation logic and local configuration model while excluding the original per-account runtime folders from the private deployment.

## Highlights

- one canonical codebase extracted from a multi-account private deployment
- bearer token via env var or local token file
- task, wheel, reward, tap, and miner-market flows in one script
- reserve-aware auto-buy logic driven by local config
- local JSON logging for operational traceability

## Tech stack

- Python 3.10+
- requests
- colorama

## Project structure

- `bot_allinone_v2.py` - main automation script
- `config.example.json` - example tuning values for reserve logic and cycle timing
- `token.txt.example` - example local token file placeholder
- `.env.example` - optional environment-based token usage
- `docs/CONFIG.md` - config notes
- `docs/QUICKSTART.md` - copy-pasteable local bootstrap steps

## Local-only files

The public repo intentionally excludes:

- real `token.txt`
- `activity_log.json`
- `potential_actions.json`
- `config.json`
- the original `acc1..acc4` private deployment folders

## Quick start

### Option A: token file
```bash
cp token.txt.example token.txt
python3 bot_allinone_v2.py
```

### Option B: environment variable
```bash
export ROLLERCOIN_BEARER_TOKEN="replace-me"
python3 bot_allinone_v2.py
```

### Optional config bootstrap
```bash
cp config.example.json config.json
```

## What the bot automates

A typical cycle looks like this:

1. load auth token
2. fetch user and balance data
3. try daily reward claim
4. recharge energy and collect taps
5. inspect and claim tasks
6. spin the wheel if balance allows
7. evaluate miner purchases or upgrades based on payback heuristics
8. write local activity snapshots
9. sleep until the next cycle

## Documentation

- `docs/QUICKSTART.md`
- `docs/CONFIG.md`

## Scope and limitations

- This repo is a public-safe showcase of the core bot logic.
- Real tokens, account snapshots, and original multi-account folders are intentionally excluded.
- Purchase behavior still depends on local config and live in-game economics.

## Security notes

- Never commit real bearer tokens.
- Never commit per-account runtime snapshots.
- If you run multiple accounts, keep separate working directories instead of reusing one runtime folder.

## Disclaimer

Shared for educational and automation-architecture reference. Use it responsibly and according to the target platform's rules and your own risk tolerance.
