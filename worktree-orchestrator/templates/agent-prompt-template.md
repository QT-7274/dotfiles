# Agent Prompt — wt-<NN>-<NAME>

## Role
You are responsible for worktree `wt-<NN>-<NAME>` on branch `feat/<PROJECT_NAME>-<NAME>`.

## First Action
`cd` into your worktree directory: `<WORKTREE_PATH>`

## Exclusive Owner Scope
Files only YOU may define interfaces/contracts in:
- <FILE_LIST>

Other agents MUST NOT rewrite public contracts in these files.

## Can Also Modify
- <FILE_LIST> (non-contract changes only)

## Cannot Touch
- <FILE_LIST>

## Required Deliverables
<!-- What this agent must complete. Derived from requirements. -->

## Completion Definition
<!-- How to know the work is done. -->

## Recommended Approach
<!-- Filled by orchestrator based on stream type:
  Foundation: explore code → implement → self-review edge cases
  Shared contract: same + thorough code review
  Consumer: explore → implement → self-review
  Final integrator: explore all merged code → wire → full review + edge cases
-->

## Do NOT
- Modify files outside your allowed list
- Redefine contracts owned by other worktrees
- Skip the delivery report at the end

## References
- Read `00-shared-context.md` for project background and delivery template
- Read your taskbook at `worktree-taskbooks/<NN>-<NAME>.md` for detailed scope
