---
name: agent-docs-upgrader
description: Audits, rewrites, and creates AGENTS.md and CLAUDE.md as concise AI-agent operating manuals for any codebase. Use when the user asks to improve, fix, modernize, align, create, review, or deduplicate AGENTS.md, CLAUDE.md, Claude Code instructions, Codex/Gemini agent docs, or project AI context files.
allowed-tools: 
disable: true
---

# Agent Docs Upgrader

Use this skill to turn `AGENTS.md` and `CLAUDE.md` into high-signal agent operating manuals. The goal is not more documentation; the goal is better model behavior: faster routing, fewer wrong edits, less over-reading, and clearer local conventions.

## Core theory

A good agent doc behaves like a model upgrade:

- It tells the agent **where to look first** and **where not to look unless needed**.
- It uses **progressive disclosure**: root doc routes; repo/module docs handle local rules; large specs/docs are opt-in.
- It prefers **decision tables and short real examples** over long prose.
- It keeps strong rules rare and pairs every “don’t” with the correct “do”.
- It prevents stale context by naming the source of truth and warning about generated or historical docs.

A bad agent doc is worse than no doc when it is stale, global, verbose, contradictory, or forces the agent to read huge docs for small edits.

## When invoked

First determine the requested mode:

| User intent | Mode |
|---|---|
| “review / audit / do these comply?” | Audit only; do not edit unless asked |
| “improve / fix / rewrite / create” | Edit existing files; create missing files only when needed |
| “make these consistent” | Drift repair across `AGENTS.md` / `CLAUDE.md` |
| “multi-repo workspace” | Enter the multi-repo document decision gate first; do not create or omit sub-repo docs until the user chooses |
| “single repo” | Build one concise repo operating manual |

If the user asks for edits, proceed without asking for confirmation unless you enter the multi-repo document decision gate, or there is a real ambiguity that tools cannot resolve.

## Multi-repo document decision gate

This is a hard gate, not an advisory step. After identifying the workspace shape, if the workspace contains multiple independent Git repositories, multiple independently runnable apps/services, or a root directory that behaves like a collection of repos rather than one repo, you must pause before creating, rewriting, or omitting sub-repo agent documents.

Before the user chooses, you may only scan, audit, and explain the risk; you must not write `AGENTS.md`, `CLAUDE.md`, or sub-repo agent documents.

Ask with numbered options and explicitly wait for the user choice:

```md
I detected that this workspace contains multiple independent repositories/services. Please choose the Agent document strategy first:

[1] Maintain only root `AGENTS.md` and `CLAUDE.md` as concise routing documents; do not create sub-repo docs.
[2] Create or update mirrored `AGENTS.md` and `CLAUDE.md` for the sub-repos I specify; keep root docs for routing only.
[3] Create or update mirrored `AGENTS.md` and `CLAUDE.md` for all detected sub-repos; keep root docs for routing only.

Reply with 1, 2, or 3. If you choose 2, include the target sub-repo paths.
```

HALT: Do not continue drafting or writing any agent document until the user replies with a choice.

Skip this gate only when the user has already specified the strategy in this request, such as “only edit root docs,” “create sub-repo docs for `repo-a/` and `repo-b/`,” or “create Agent docs for all sub-repos.” Generic requests such as “update the docs” or “fix these Agent docs” are not authorization.

Ask this before drafting a long root document. The 100-line limit is a warning signal, not the first decision point. If sub-repo agent docs already exist, update them after the user chooses the corresponding strategy instead of duplicating their details in the root document.

## Discovery workflow

1. Find existing agent docs: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules`, `.github/copilot-instructions.md`, `CODEBUDDY.md`.
2. Identify workspace shape: single repo, monorepo, package workspace, or multiple independent git repos.
3. Inspect only high-signal project facts: package manager, build/test/lint commands, main frameworks, API layer, state layer, i18n, generated code, and spec directories.
4. Detect stale or misleading context: old paths, renamed repos, wrong package manager, obsolete commands, duplicated tool blocks, unconditional “read all docs” instructions.
5. Decide the doc hierarchy: root doc routes work; repo doc explains local coding rules; module docs exist only for complex subsystems; large `docs/`, `specs/`, `openspec/`, `features/`, and `adr/` directories are referenced by trigger, not loaded by default.

Avoid reading every markdown file. The doc you create should reduce future exploration, not encode your current exploration path.

## Audit rubric

Score each candidate document against this checklist:

| Criterion | Good | Bad |
|---|---|---|
| Routing | Agent can choose the right repo/module in under 30 seconds | Agent must browse docs or guess |
| Length | Usually 60–150 lines for an entry doc | Long essay, copied architecture doc, or tool manual |
| Specificity | Names real directories, commands, APIs, patterns | Generic “write clean code” advice |
| Progressive disclosure | Big docs/specs are trigger-based | “Always read all docs first” |
| Decisions | Tables resolve common ambiguity | Long paragraphs of caveats |
| Examples | 3–10 line real project snippets | Abstract pseudocode or huge code blocks |
| Rules | Few strong rules, each with reason | Wall of MUST/NEVER warnings |
| Alternatives | Every “don’t” says what to do instead | Prohibitions with no safe path |
| Freshness | Matches current repo structure | Old paths, old SDK names, old commands |
| Drift | Mirror files are clearly synchronized | `AGENTS.md` and `CLAUDE.md` disagree |

## Rewrite strategy

### Root doc for multi-repo workspaces

Use this structure:

```md
# AGENTS.md — <workspace-name>

> Multi-repo routing entry. Pick the right repo first; do not load large docs for small edits.

## Workspace map

| Directory | Role | Use when | Entry doc |
|---|---|---|---|
| `<repo-a>/` | <role> | <task trigger> | `<repo-a>/AGENTS.md` |

## Startup rules

| Situation | Do |
|---|---|
| Task names a repo/path | Read that repo entry only |
| Unsure which repo owns it | Use the routing table, then inspect minimal files |
| New feature / breaking change | Read the relevant spec process |
| Small copy/style/config fix | Do not load broad architecture docs |

## Global working agreements

- Keep diffs small and scoped to the target repo.
- Prefer current code over generated docs when they disagree.
- Do not mix similarly named repos without checking their purpose.
```

### Root-to-subrepo linking rule

When the user chooses to create or maintain sub-repo agent documents, the root `AGENTS.md` and `CLAUDE.md` must reference those documents in the workspace map.

Each sub-repo row should include:

- the sub-repo directory;
- its role;
- when to use it;
- the path to its local agent document.

Do not create sub-repo `AGENTS.md` / `CLAUDE.md` files without adding them to the root routing table. The root document should route; the sub-repo document should explain local rules.

### Repo entry doc

Use this structure:

```md
# AGENTS.md — <repo-name>

> <one-sentence repo purpose and agent instruction>

## Project map

| Path | Purpose | Read when |
|---|---|---|
| `src/api/` | API wrappers | API calls change |

## Common workflows

| Task | Start here | Notes |
|---|---|---|
| Add UI behavior | `<path>` | Follow existing component pattern |

## Local rules

- Do not <bad pattern>; use `<good pattern>` because <reason>.

## Short examples

```ts
// 3–10 lines copied or adapted from real local patterns.
```

## Commands

| Command | Use |
|---|---|
| `<cmd>` | <when to run> |

## Large docs and specs

| Trigger | Read |
|---|---|
| New capability or breaking change | `<spec-dir>/AGENTS.md` |
```

## CLAUDE.md / AGENTS.md synchronization rule

By default, keep `CLAUDE.md` and `AGENTS.md` **identical**. This reduces drift and prevents different agents from reading different project rules.

Only isolate small platform-specific sections when the user explicitly asks for platform-specific behavior; shared rules should still remain identical.

## What to include

Include only information that changes agent actions:

- Correct repo/module routing.
- Real commands for install, dev, lint, test, typecheck, generation.
- High-frequency source directories.
- API/data/state/i18n patterns.
- Generated files and files not to edit by hand.
- Safety boundaries: migrations, schemas, public API shapes, auth, billing, data deletion.
- Spec/doc triggers.
- Short examples that encode local style.

## What to cut

Cut or move out of the entry doc:

- Generic software advice.
- Full architecture essays.
- Full directory trees.
- Long tool manuals.
- Historical explanations that do not affect current edits.
- Repeated warnings without a safe alternative.
- “Always read every doc first” instructions.
- Stale repository names, old SDK labels, and obsolete commands.

## Decision tables to add

Add only tables relevant to the repo:

### Context loading

| Task | Load by default | Load only if needed |
|---|---|---|
| Small bug/copy/style fix | Entry doc + touched files | Architecture docs |
| New feature | Entry doc + nearby code | Spec/ADR process |
| API shape change | API definitions + consumers | Cross-repo impact docs |
| Schema change | Entity/model + migrations | Historical proposals |

### Change safety

| Change | Required check |
|---|---|
| Public API response shape | Consumers and tests |
| Database schema | Migration and rollback path |
| Shared utility | Callers or impact analysis |
| Generated code | Generator/source file, not generated output |
| i18n copy | Source locale and extraction/generation command |

## Rules for “don’t” statements

Write prohibitions in this format:

```md
- Do not call `fetch` directly; use `src/api/request.ts` so auth, errors, and telemetry stay consistent.
```

Bad:

```md
- NEVER use fetch.
```

The good version tells the agent the safe route and why it matters.

## Example quality bar

Examples should be:

- Real or faithful to current code.
- 3–10 lines.
- Focused on one reusable pattern.
- Free of secrets and private tokens.
- Short enough to copy mentally, not a full component/service.

Prefer examples for API calls, state updates, i18n, migrations, tests, and generated-code workflows.

## Completion checklist

Before claiming the doc is done, verify:

- Paths in tables exist or are intentionally documented as external.
- Commands exist in package scripts, Makefiles, or repo docs.
- `AGENTS.md` and `CLAUDE.md` are identical by default, unless the user explicitly requested platform-specific sections.
- If sub-repo agent docs were created or maintained, the root workspace map references them.
- Root docs route; repo docs instruct; large docs are trigger-based.
- No default instruction forces reading huge docs for small edits.
- Each “do not” has a “use this instead”.
- The doc says what to do when generated docs conflict with source code.
- The result is shorter than the old doc unless missing critical context required expansion.

## Response format

When reporting back, keep it brief:

```md
- **Updated**: `<files>`
- **Main changes**: routing, stale paths, decision tables, examples, doc-loading policy
- **Remaining risk**: any unresolved ambiguity or missing command you could not verify
```
