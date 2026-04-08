---
name: bmad-worktree-orchestrator
description: Use when executing a multi-worktree parallel development workflow from BMAD planning artifacts (epics, architecture). Triggers: 'start worktree development', 'run worktree orchestration', 'execute worktree plan'.
allowed-tools: 
disable: false
---

# Multi-Worktree Orchestrator

Orchestrate parallel development across isolated git worktrees. Takes BMAD planning artifacts as input, generates execution artifacts (worktree plan, agent prompts, taskbooks), creates branches and worktrees, dispatches sub-agents in dependency-ordered batches, gates each batch on human approval, and merges results to a shared develop branch.

This skill does NOT replace BMAD planning skills. It picks up where they leave off.

## When to Use

- Project has 2+ independent work streams that can run in parallel
- BMAD planning artifacts (epics, architecture) already exist
- Work is large enough to benefit from isolated worktrees and parallel agents

## When NOT to Use

- Single-stream work → use `bmad-quick-dev` directly
- No BMAD artifacts exist yet → run `bmad-create-epics-and-stories` and `bmad-create-architecture` first
- Fewer than 2 worktrees needed → overhead is not worth it

## Startup: Check for Existing State

Before anything else, check if a `worktree-progress.md` exists in the project's BMAD output directory.

**If found:**
1. Read `current_phase` and `current_batch`.
2. Tell the user: "Found an in-progress worktree workflow at Batch N, status: X. Continue?"
3. On confirmation, jump to the matching phase below.

**Resume points:**

| Last State | Action |
|-----------|--------|
| Phase 0–2 (prepare) | Restart preparation, overwrite old files |
| Step 4.1 (worktree setup) | Detect existing worktrees, skip created ones |
| Step 4.2 (agents dispatched) | Check each worktree: delivery report exists → done. Commits but no report → ask user: re-dispatch, continue partial, or manual fix. No commits → re-dispatch |
| Step 4.4–4.5 (review/gate) | Re-run review from current diffs, re-present gate summary |
| Phase 5 (final) | Same as Step 4.2 logic |

**If not found:** Start from Phase 0.

### Progress File Format

`worktree-progress.md` tracks all state. Markers: `[ ]` not started, `[~]` in progress, `[x]` merged, `[!]` failed.

Status flow per worktree:

```
not-started → worktree-created → agent-dispatched → agent-done
  → review-done → awaiting-approval → merged
agent-dispatched → agent-failed → retry-pending → agent-dispatched
```

## Phase 0: Validate BMAD Artifacts

Scan for required planning outputs:

| Artifact | Source Skill | Required |
|----------|-------------|----------|
| Epics (stories + acceptance criteria) | `bmad-create-epics-and-stories` | Yes |
| Architecture doc (modules, tech choices) | `bmad-create-architecture` | Yes |
| Tech spec / PRD | `bmad-create-prd` | Recommended |

**Search strategy:** Scan `_bmad-output/`, `docs/`, project root. Match by filename pattern (`*epic*`, `*architecture*`, `*tech-spec*`, `*prd*`). If auto-discovery fails, ask the user to point to files directly.

If a required artifact is missing, stop and tell the user which BMAD skill to run first. Do not proceed.

### Small Project Shortcut

After reading the epics, estimate the number of independent work streams. If only 1 worktree would be generated, tell the user:

> "This project looks small enough for a single work stream. `bmad-quick-dev` would be simpler and faster. Want to use that instead, or continue with the full orchestrator?"

Proceed only if the user confirms the orchestrator.

## Phase 1: Generate Worktree Plan

**Input:** Epics + architecture found in Phase 0.

**Process:**

1. Read all stories and acceptance criteria from the epics file.
2. Identify dependency layers: stories that define shared contracts (foundation) vs. stories that consume them.
3. Find high-conflict files using these heuristics:
   - Check the architecture doc for module-to-file mappings.
   - If not available, scan codebase directories and match story keywords to file/directory names.
   - Ask the user to confirm ambiguous file-to-story mappings.
4. Assign each high-conflict file to exactly one owner worktree.
5. Group stories into worktrees. Each worktree gets a coherent slice with clear file boundaries.
6. Order worktrees into batches: foundation first, then consumers after their dependencies merge.
7. Designate one worktree as final-integrator (runs in Phase 5, not a regular batch).

**Output:** Generate `worktree-plan.md` in the BMAD output directory using the template in `templates/worktree-plan-template.md`.

Present the plan to the user for confirmation before proceeding.

## Phase 2: Generate Agent Artifacts

**Input:** Worktree plan from Phase 1 + original epics + architecture.

For each worktree in the plan, generate:

### 1. Shared context (`00-shared-context.md`)
One file shared by all agents. Use template: `templates/shared-context-template.md`

Fill in project background, global goals, shared conventions, universal constraints. Include the unified delivery template verbatim.

### 2. Agent prompts (`agent-prompts/<NN>-<name>-prompt.md`)
One per worktree. Use template: `templates/agent-prompt-template.md`

Fill in: role, owner scope, forbidden files, deliverables, completion definition. Set the recommended skill sequence based on worktree type:

| Worktree Type | Identification | Recommended Skills |
|--------------|----------------|-------------------|
| Foundation (batch 1) | Defines shared contracts, no upstream deps | Explore agent → `bmad-quick-dev` → `bmad-review-edge-case-hunter` → `simplify` (if code scatters) |
| Shared contract (batch 2) | Downstream worktrees depend on it | Same as foundation + `bmad-code-review` |
| Consumer (batch 3+) | Only consumes contracts | Explore agent → `bmad-quick-dev` → `bmad-review-edge-case-hunter` |
| Final integrator | Merges all, resolves wiring | Explore agent → `bmad-quick-dev` → `bmad-code-review` (required) → `bmad-review-edge-case-hunter` → `simplify` (if messy) |

"Explore agent" = Agent tool with `subagent_type: "Explore"` for read-only codebase navigation.

### 3. Worktree taskbooks (`worktree-taskbooks/<NN>-<name>.md`)
One per worktree. Contains: branch info, merge target, allowed/forbidden files, deliverables with acceptance criteria, completion definition. Derived from the worktree plan and epics.

---

## Gate 0: Human Reviews Generated Artifacts

**STOP.** Present to the user:

> Generated artifacts:
> - `worktree-plan.md` — N worktrees in M batches
> - `00-shared-context.md`
> - N agent prompts in `agent-prompts/`
> - N worktree taskbooks in `worktree-taskbooks/`
>
> Please review. Confirm to proceed to execution, or request changes.

Do NOT proceed until the user confirms. If changes requested, revise and re-present.

Write initial `worktree-progress.md` with all worktrees in `not-started` state.

## Phase 3: Setup Branches and Worktrees

1. Create the develop branch from main:

```bash
git switch -c feat/<project>-develop
```

If the branch already exists:

```bash
git switch feat/<project>-develop
git pull --ff-only
```

2. Create worktrees for Batch 1 ONLY:

```bash
git worktree add ../wt-<name> -b feat/<project>-<name>
```

Later batches are created on demand in Step 4.1, so they branch from the latest develop.

3. Update `worktree-progress.md`: set `current_phase: execute`, `current_batch: 1`, mark Batch 1 worktrees as `worktree-created`.

## Phase 4: Batch Dispatch Loop

Repeat for each batch in the worktree plan:

### Step 4.1: Create or Sync Worktrees

**New worktrees** (not yet created):

```bash
git switch feat/<project>-develop
git worktree add ../wt-<name> -b feat/<project>-<name>
```

**Existing worktrees** (created earlier, need sync):

```bash
cd ../wt-<name>
git merge --no-ff feat/<project>-develop
```

Update progress: mark worktrees as `worktree-created`.

### Step 4.2: Dispatch Agents

**Calls:** `superpowers:dispatching-parallel-agents`

For each worktree in the batch, launch a sub-agent via the Agent tool:

- **Batch with 2+ worktrees:** Use `run_in_background: true` for each agent. All run concurrently.
- **Batch with 1 worktree:** Use foreground (default) agent.

Each agent prompt includes:
- The worktree's `agent-prompts/<NN>-<name>-prompt.md`
- The worktree's `worktree-taskbooks/<NN>-<name>.md`
- The `00-shared-context.md`
- Instruction: first action is `cd <worktree-path>`

Update progress: mark worktrees as `agent-dispatched`.

Wait for all background agents to complete before proceeding.

### Step 4.3: Collect Delivery Reports

Each agent returns a structured delivery report (format defined in `00-shared-context.md`).

For each agent:
1. Verify the delivery report is well-formed (has all required sections).
2. If report is missing or malformed, mark as `agent-failed`.
3. If report exists, mark as `agent-done`.

Append delivery summaries to `worktree-progress.md`.

### Step 4.4: Code Review

**Calls:** `bmad-code-review`

For each worktree branch:

```bash
git diff feat/<project>-develop...feat/<project>-<name>
```

Review checks:
1. **Boundary violations:** Modified files not in allowed list? Cross-reference owner map.
2. **Contract conflicts:** Redefined contracts owned by another worktree?
3. **Code quality:** Bugs, edge cases, style.

Update progress: mark worktrees as `review-done`.

### Step 4.5: Gate N — Human Approval

**STOP.** Present batch summary:

> **Batch N complete. Awaiting approval.**
>
> | Worktree | Files | New Artifacts | Tests | Risks |
> |----------|-------|---------------|-------|-------|
> | wt-NN-xxx | N | N | Pass/Fail | N |
>
> **Code Review:** (summary per worktree)
> **Boundary Check:** (violations or clean)
> **Failed agents:** (list if any, with retry/skip/manual options)
>
> Approve merge to develop?

**On approval:** Merge in worktree number order:

```bash
git switch feat/<project>-develop
git merge --no-ff feat/<project>-<name>
```

If merge conflict: `git merge --abort`, report conflicting files with owner map cross-reference, wait for user resolution.

If same-batch conflict: flag as ownership gap in the plan.

Update progress: mark worktrees as `merged`, increment `current_batch`, update `updated_at`.

**On rejection:** User can request re-dispatch, manual fixes, or changes. Adjust and re-present gate.

Repeat loop for next batch.

## Phase 5: Final Integration

### Step 5.1: Dispatch Final-Integrator Agent

Create the final worktree (if not yet created):

```bash
git switch feat/<project>-develop
git worktree add ../wt-<name>-final -b integration/<project>-final
```

Or sync if it exists:

```bash
cd ../wt-<name>-final
git merge --no-ff feat/<project>-develop
```

Dispatch a single foreground agent with the final-integrator prompt. This agent's job:
- Resolve cross-worktree wiring (connect independently built pieces)
- Fix conflicts in split-ownership files (initial vs. final changes)
- Run full regression

Its skill chain is stricter: `bmad-code-review` is REQUIRED.

### Step 5.2: Regression Verification

**Calls:** `superpowers:verification-before-completion`

The final agent produces a regression matrix:

```markdown
| Feature / Command | Executes | Output Correct | Integration Wired |
|-------------------|----------|----------------|-------------------|
| (feature) | Pass/Fail | Pass/Fail | Pass/Partial/Fail |
```

### Step 5.3: Final Gate

**STOP.** Present to user:

> **Final integration complete.**
>
> - All N worktrees merged to develop
> - Cross-worktree wiring resolved
> - Regression: X/Y items pass
> - Uncovered: (list)
>
> Approve branch closeout?

**On approval:** Call `superpowers:finishing-a-development-branch` for merge, PR, or cleanup.

Update progress: set `current_phase: complete`.

## Error Handling

### Sub-Agent Failure

Agent fails, returns incomplete output, or reports failing tests:
- Do not block other agents in the same batch.
- Mark worktree as `agent-failed` in progress file.
- At Gate time, present options: **Retry** (re-dispatch), **Manual fix** (user intervenes), **Defer** (skip, leave to final integrator).

### Merge Conflict

`git merge --no-ff` fails:
1. `git merge --abort`
2. Report conflicting files.
3. Cross-reference owner map: sole-owner conflict = rebase issue; multi-branch conflict = boundary violation.
4. Wait for user resolution.

### Boundary Violation

Detected in Step 4.4:
- Compare diff file list against worktree's allowed files.
- If file not in allowed list, find the real owner from the owner map.
- Report as warning in Gate summary. Do not auto-block.

## Practical Limits

Recommended: 8–10 worktrees, 3–4 batches maximum. For larger projects, split into multiple orchestrator runs covering different epic groups.

## What This Skill Does NOT Do

- **BMAD planning.** Run `bmad-create-epics-and-stories` and `bmad-create-architecture` first.
- **Conflict resolution.** Detects and reports. Humans resolve.
- **Sub-agent micromanagement.** Sets up prompts and constraints. Agents decide how to implement.
- **Push to remote.** All git operations are local. User decides when to push.
