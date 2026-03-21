# rollercoin

Python automation script for a RollerCoin tap / upgrade workflow with balance checks, task claims, wheel spins, daily reward attempts, energy recharge, miner upgrade heuristics, and local activity logging.

This public candidate is prepared as a **safe showcase version** of the original working project. The private multi-account deployment folders were collapsed into a single reusable codebase, while live bearer tokens, per-account runtime JSON, and account-specific logs were excluded.

## What is included

- `bot_allinone_v2.py` - main automation script
- `config.example.json` - example tuning values for reserve logic and cycle timing
- `token.txt.example` - example local token file placeholder
- `.env.example` - optional environment-based token usage
- `requirements.txt` - minimal dependencies
- `LICENSE`

## What is intentionally excluded

- `acc1..acc4` account folders from the private deployment
- real `token.txt` files
- `activity_log.json`
- `potential_actions.json`
- per-account runtime data

## Project behavior

The script talks to the RollerCoin tap API and automates a cycle roughly like this:

1. load auth token from `ROLLERCOIN_BEARER_TOKEN` or `token.txt`
2. fetch user profile and balance
3. try daily reward claim on schedule
4. recharge energy and collect taps
5. inspect tasks and claim eligible ones
6. check wheel balance and spin if available
7. evaluate miner purchases/upgrades based on payback heuristics
8. persist local activity snapshots to JSON files
9. sleep until the next cycle

## Installation

```bash
pip install -r requirements.txt
```

## Setup

### Option A: token file
```bash
cp token.txt.example token.txt
```
Then paste your bearer token into `token.txt`.

### Option B: environment variable
```bash
export ROLLERCOIN_BEARER_TOKEN="replace-me"
```

### Optional config override
The script auto-creates `config.json` if it does not exist. If you want a starting template first:

```bash
cp config.example.json config.json
```

## Run

```bash
python3 bot_allinone_v2.py
```

## Notes on local files

At runtime the script may create:

- `activity_log.json`
- `potential_actions.json`
- `config.json`

These are intentionally ignored from version control.

## Security notes

- Never commit real bearer tokens.
- Never commit per-account runtime snapshots.
- If you run multiple accounts, keep separate working directories instead of reusing one runtime folder.

## Disclaimer

Shared for educational and automation-architecture reference. Use it responsibly and according to the target platform's rules and your own risk tolerance.
