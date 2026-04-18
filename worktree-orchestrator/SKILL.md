---
name: worktree-orchestrator
description: "Use when a project needs parallel development across multiple git worktrees. Triggers: 'start worktree development', 'run worktree orchestration', 'parallel worktree workflow'. Works with any requirement docs."
allowed-tools:
disable: false
---


# Multi-Worktree Orchestrator

Split a project into parallel work streams, each in its own git worktree, with dependency-ordered execution and human-gated merges.

## When to Use

- Project has 2+ independent work streams that benefit from parallel isolation
- Requirements are clear enough to split into batches with defined dependencies
- You want structured agent dispatch with review gates between batches

## When NOT to Use

- Single work stream — just work directly, no orchestration needed
- Requirements are vague — clarify first, then come back
- Fewer than 2 worktrees needed — overhead is not worth it

---

## Startup: Check for Existing State

Before anything else, look for `worktree-progress.md` in the project root or docs directory.

**If found:** Read `current_phase` and `current_batch`. Ask user: "Found an in-progress workflow at Batch N. Continue?" On confirmation, jump to matching phase.

**Resume points:**

| Last State | Action |
|-----------|--------|
| Phase 0–2 (prepare) | Restart preparation, overwrite old files |
| Step 4.1 (worktree setup) | Skip existing worktrees, create missing ones |
| Step 4.2 (agents running) | Delivery report exists → done. Commits but no report → ask user. No commits → re-dispatch |
| Step 4.4–4.5 (review/gate) | Re-run review, re-present gate summary |
| Phase 5 (final) | Same as Step 4.2 logic |

**If not found:** Start from Phase 0.

### Progress Markers

`[ ]` not started · `[~]` in progress · `[x]` merged · `[!]` failed

Status flow:
```
not-started → worktree-created → agent-dispatched → agent-done
  → review-done → awaiting-approval → merged
agent-dispatched → agent-failed → retry-pending → agent-dispatched
```

---

## Phase 0: Confirm Requirements Are Ready

You need requirements clear enough to split into parallel work streams. Acceptable inputs include ANY of:

- Epics / user stories with acceptance criteria
- PRD or tech spec
- Architecture document with module breakdown
- A well-structured issue list or task breakdown
- Even a clear verbal description from the user

**What to check:**

1. Can you identify 2+ independent work streams?
2. Are there shared contracts or interfaces between streams?
3. Is the scope per stream clear enough to write a task description?

**If requirements are unclear:**
Ask the user targeted questions to clarify. Focus on:
- What are the major pieces of work?
- Which pieces depend on each other?
- Which files or modules does each piece touch?

Do not proceed until you can answer: "What are the streams, what order, and who owns what files."

### Small Project Shortcut

If only 1 work stream emerges, tell the user: "This looks like a single stream — no need for worktree orchestration. Want to proceed directly?" Skip to normal development if confirmed.

---

## Phase 1: Generate Worktree Plan

**Input:** Whatever requirements you confirmed in Phase 0.

**Process:**

1. List all work streams and their scope.
2. Identify dependencies: which streams define shared interfaces (foundation), which consume them.
3. Find high-conflict files — files multiple streams would modify:
   - Check any architecture doc for module-to-file mappings.
   - Scan codebase directories and match to work streams.
   - Ask user to confirm ambiguous mappings.
4. Assign each high-conflict file to exactly one owner stream.
5. Order streams into batches: foundation first, consumers after.
6. Designate a final-integrator stream if there are 3+ batches.

**Output:** Generate `worktree-plan.md` using template: `templates/worktree-plan-template.md`

Present to user for confirmation.

---

## Phase 2: Generate Agent Artifacts

For each worktree in the plan, generate:

### 1. Shared context (`00-shared-context.md`) — one file for all agents

Use template: `templates/shared-context-template.md`

Contents: project background, global goals, shared conventions, constraints, unified delivery template.

### 2. Agent prompts (`agent-prompts/<NN>-<name>-prompt.md`) — one per worktree

Use template: `templates/agent-prompt-template.md`

Contents: role, owner scope, forbidden files, deliverables, completion definition, recommended approach.

**Approach recommendations by stream type:**

| Stream Type | Recommendation |
|------------|---------------|
| Foundation (batch 1) | Explore code first (read-only) → implement → self-review edge cases |
| Shared contract (batch 2) | Same + thorough code review (changes affect many consumers) |
| Consumer (batch 3+) | Explore → implement → self-review |
| Final integrator | Explore all merged code → wire pieces together → full code review (required) → edge case review |

### 3. Worktree taskbooks (`worktree-taskbooks/<NN>-<name>.md`) — one per worktree

Contents: branch info, merge target, allowed/forbidden files, deliverables with acceptance criteria, done definition.

---

## Gate 0: Human Reviews Generated Artifacts

**STOP.** Present:

> Generated:
> - `worktree-plan.md` — N worktrees in M batches
> - `00-shared-context.md`
> - N agent prompts
> - N worktree taskbooks
>
> Please review. Confirm to proceed, or request changes.

Do NOT continue until user confirms. Write initial `worktree-progress.md`.

---

## Phase 3: Setup Branches and Worktrees

1. Create develop branch:

```bash
git switch -c feat/<project>-develop
```

If it exists: `git switch feat/<project>-develop && git pull --ff-only`

2. Create worktrees for **Batch 1 only**:

```bash
git worktree add ../wt-<name> -b feat/<project>-<name>
```

Later batches are created on demand in Step 4.1 so they branch from latest develop.

3. Update `worktree-progress.md`: `current_phase: execute`, `current_batch: 1`.

---

## Phase 4: Batch Dispatch Loop

Repeat for each batch:

### Step 4.1: Create or Sync Worktrees

**New:** `git worktree add ../wt-<name> -b feat/<project>-<name>` from develop HEAD.

**Existing:** `cd ../wt-<name> && git merge --no-ff feat/<project>-develop`

### Step 4.2: Dispatch Agents

For each worktree in the batch, launch a sub-agent:

- **2+ worktrees in batch:** Use `run_in_background: true` for parallelism.
- **1 worktree:** Use foreground agent.

Each agent gets: its prompt + its taskbook + shared context + instruction to `cd` into its worktree first.

Wait for all agents to complete.

### Step 4.3: Collect Delivery Reports

Each agent returns a structured report (format in `00-shared-context.md`):
- Modified files, new artifacts, risks, verification results, handoff notes.

Missing or malformed report → mark `agent-failed`.

### Step 4.4: Code Review

For each branch, review the diff against develop:
1. **Boundary violations:** Modified files not in allowed list?
2. **Contract conflicts:** Redefined interfaces owned by another worktree?
3. **Code quality:** Bugs, edge cases, style.

### Step 4.5: Gate N — Human Approval

**STOP.** Present:

> **Batch N complete.**
>
> | Worktree | Files | Artifacts | Tests | Risks |
> |----------|-------|-----------|-------|-------|
> | wt-NN-xxx | N | N | Pass/Fail | N |
>
> **Review summary:** (per worktree)
> **Boundary check:** (violations or clean)
> **Failed agents:** (if any — retry/skip/manual options)
>
> Approve merge?

**On approval:** Merge in worktree number order:

```bash
git switch feat/<project>-develop
git merge --no-ff feat/<project>-<name>
```

Merge conflict → `git merge --abort`, report files, cross-reference owner map, wait for user.

Same-batch conflict → flag as ownership gap.

Update progress, move to next batch.

---

## Phase 5: Final Integration

### Step 5.1: Dispatch Final-Integrator

Create or sync the final worktree. Dispatch a single foreground agent:
- Wire independently built pieces together
- Fix split-ownership file conflicts
- Run full regression
- Code review is REQUIRED for this agent

### Step 5.2: Regression Verification

Final agent produces:

```markdown
| Feature / Command | Executes | Output OK | Integrated |
|-------------------|----------|-----------|------------|
| ... | Pass/Fail | Pass/Fail | Pass/Partial/Fail |
```

### Step 5.3: Final Gate

**STOP.** Present regression results. On approval, handle branch closeout (merge to main, PR, or cleanup).

Update progress: `current_phase: complete`.

---

## Error Handling

**Sub-agent failure:** Don't block other agents. Mark `agent-failed`. At gate, offer: retry, manual fix, or defer to final integrator.

**Merge conflict:** Abort, report files, cross-reference owner map (sole-owner = rebase issue, multi-branch = boundary violation). Wait for user.

**Boundary violation:** Compare diff against allowed files. Report as warning. Don't auto-block.

## Practical Limits

8–10 worktrees, 3–4 batches max. Larger projects: split into multiple orchestrator runs.

## What This Skill Does NOT Do

- **Requirements gathering.** Clarifies readiness, but doesn't create PRDs or epics from scratch.
- **Conflict resolution.** Detects and reports. Humans resolve.
- **Sub-agent micromanagement.** Sets up prompts and constraints. Agents decide how to implement.
- **Push to remote.** All git ops are local. User decides when to push.
