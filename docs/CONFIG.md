# CONFIG

The public repo ships with `config.example.json` so the auto-buy and reserve logic can be understood without exposing live local runtime files.

## Main config keys

### `RESERVE_MODE`
Determines how much balance should be protected from spending.

Example value:
- `auto_topk_payback`

## `RESERVE_MANUAL_AMOUNT`
Fallback reserve amount if you want a fixed manual reserve instead of a heuristic strategy.

## `AUTO_TOPK_K`
How many top candidate upgrade opportunities should be considered in the automatic reserve calculation.

## `ROI_HOURS_THRESHOLD`
Upper bound for acceptable payback/ROI time when evaluating miner actions.

## `RESERVE_SAFETY_FACTOR`
Multiplier used to make the reserve calculation more conservative.

## `MULTI_BUY`
Whether the script is allowed to perform multiple purchase actions in one cycle.

## `MAX_ACTIONS_PER_CYCLE`
Hard cap for how many purchase/upgrade actions can happen in a single loop.

## `RECOMPUTE_BETWEEN_PURCHASES`
Whether the candidate evaluation should be recalculated after each purchase instead of acting on one stale ranking.

## `SLEEP_SECONDS`
How long the bot should wait between cycles.

## `AUTO_BUY_ENABLED`
Global on/off switch for the purchase automation path.

## Practical use

A reasonable safe workflow is:

1. copy `config.example.json` to `config.json`
2. start with conservative values
3. observe `activity_log.json`
4. tighten or loosen reserve settings only after seeing how the script behaves with your account balance and miner state
