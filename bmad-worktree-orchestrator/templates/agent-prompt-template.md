# Agent Prompt — wt-<NN>-<NAME>

## Role
You are responsible for worktree `wt-<NN>-<NAME>` on branch `feat/<PROJECT_NAME>-<NAME>`.

## First Action
`cd` into your worktree directory: `<WORKTREE_PATH>`

## Exclusive Owner Scope
Files only YOU may define contracts in:
- <FILE_LIST>

Other agents MUST NOT rewrite public contracts in these files.

## Can Also Modify
- <FILE_LIST> (non-contract changes only)

## Cannot Touch
- <FILE_LIST>

## Required Deliverables
<!-- Derived from story acceptance criteria -->

## Completion Definition
<!-- How to know the work is done -->

## Recommended Skill Sequence
<!-- Filled by orchestrator based on worktree type -->

## Skills to Avoid
- `brainstorming` — slows down fixed-scope work
- `bmad-create-epics-and-stories` — planning phase, not execution

## References
- Read `00-shared-context.md` for project background and delivery template
- Read your taskbook at `worktree-taskbooks/<NN>-<NAME>.md` for detailed scope
