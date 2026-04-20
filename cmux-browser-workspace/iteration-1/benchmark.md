# Benchmark: cmux-browser (Iteration 1)

## Pass Rates

| Evaluation | with_skill | without_skill |
|---|---|---|
| navigate-and-snapshot | 100% (3/3) | 100% (3/3) |
| form-interaction | 100% (3/3) | 100% (3/3) |
| extract-data | 100% (3/3) | 100% (3/3) |
| **Overall** | **100%** | **100%** |

## Token Usage

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| Mean tokens | 32819 | 32093 | +726 |
| Total tokens | 98,457 | 96,280 | +2,177 |

## Duration (seconds)

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| Mean | 120.0s | 137.9s | -17.9s |
| Total | 360.0s | 413.8s | -53.9s |

## Tool Uses

| Metric | with_skill | without_skill | Delta |
|---|---|---|---|
| Mean | 16.0 | 17.3 | -1.3 |
| Total | 48 | 52 | -4 |

## Analyst Observations

1. **Functional correctness**: All 6 runs passed all assertions. Both skill-guided and unguided approaches successfully completed the browser automation tasks.

2. **find text reliability**: Both with_skill and without_skill encountered JavaScript exceptions with `find text` on Hacker News. This is a cmux browser limitation, not a skill issue. The skill correctly recommended fallback to `snapshot --interactive`.

3. **Selector strategy**: In form-interaction, both approaches struggled with `button[type='submit']` because the actual button lacked that attribute. The skill-guided run fell back to `button` selector; the unguided run used `eval document.querySelector('button').click()`. The skill approach was more direct.

4. **Token efficiency**: with_skill used slightly more tokens on average (+726), likely because the skill loaded the full SKILL.md into context (293 lines).

5. **Tool efficiency**: with_skill used 16 tool calls on average vs 17 without, suggesting the skill helped reduce trial-and-error.
