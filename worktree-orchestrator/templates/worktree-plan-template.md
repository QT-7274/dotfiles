# Worktree Plan

## Project
- Name: <PROJECT_NAME>
- Develop branch: feat/<PROJECT_NAME>-develop
- Base: main

## Worktrees

### wt-<NN>-<NAME>
- Branch: feat/<PROJECT_NAME>-<NAME>
- Batch: <BATCH_NUMBER>
- Depends on: [<WORKTREE_IDS>]  <!-- omit for batch 1 -->
- Scope: <WHAT_THIS_STREAM_DOES>
- Owns: [<FILES_THIS_WORKTREE_DEFINES_CONTRACTS_IN>]
- Can also modify: [<FILES_WITH_NON_CONTRACT_CHANGES>]
- Cannot touch: [<FILES_OWNED_BY_OTHER_WORKTREES>]

<!-- Repeat for each worktree -->

## Batch Execution Order
- Batch 1: [<WORKTREE_IDS>] — foundation
- Batch 2: [<WORKTREE_IDS>] — parallel
- Batch N: [<WORKTREE_IDS>] — parallel

Note: The final integrator runs in Phase 5, not as a regular batch.

## Owner Map

| File | Sole Owner | Why |
|------|-----------|-----|
| <FILE_PATH> | wt-<NN> | <REASON> |

## Merge Sequence
1. feat/<PROJECT_NAME>-<NAME_01> → feat/<PROJECT_NAME>-develop
2. feat/<PROJECT_NAME>-<NAME_02> → feat/<PROJECT_NAME>-develop
<!-- In batch order -->
