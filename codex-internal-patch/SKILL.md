---
name: codex-internal-patch
description: Patch the codex-companion plugin scripts to work with the internal Tencent codex-internal distribution, which disables the `login`, `app-server` subcommands. Run this skill after any codex plugin update that overwrites the patches. Triggers on: 'patch codex', 'codex review broken', 'codex not authenticated', 'fix codex plugin', 'codex login failed'.
allowed-tools: 
disable: true
---


# codex-internal-patch

This skill patches the `openai-codex` Claude Code plugin to work with the internal `codex-internal` binary (Tencent internal distribution), which disables the `login` and `app-server` subcommands that the upstream plugin relies on.

## Background

The `codex-companion.mjs` plugin scripts are designed for the official `@openai/codex` binary. The internal `codex-internal` binary differs in two ways:

1. `codex login status` → exit 1 ("login【内部禁用】") — uses SSO/internal auth instead
2. `codex app-server` → exit 1 ("app-server【内部禁用】") — no JSON-RPC runtime

This causes the plugin to fail at two guard checks before any review runs:
- `getCodexAvailability()`: sees `app-server` fail → returns `available: false` → all commands abort
- `getCodexLoginStatus()`: sees `login status` fail → returns `loggedIn: false` → throws "not authenticated"

And even if those pass, `runAppServerReview()` would fail trying to spawn `codex app-server`.

## What This Skill Does

Applies three patches to the plugin's lib files:

1. **`getCodexAvailability`** — treat `app-server` unavailable as non-fatal (internal distro)
2. **`getCodexLoginStatus`** — fallback: if `login status` fails but `review --help` succeeds → authenticated
3. **`executeReviewRun`** — fallback: if `runAppServerReview` throws → run `codex review --uncommitted` directly via CLI

## Instructions

### Step 1: Locate the plugin files

The files to patch are:
- `~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/lib/codex.mjs`
- `~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs`

Resolve the actual paths:
```bash
ls ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/lib/codex.mjs
ls ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs
```

### Step 2: Verify patch is needed

Check if the patches are already applied:
```bash
grep -c "internal distribution" ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/lib/codex.mjs
```

- Output `0` → patches needed, proceed
- Output `2` → already patched, skip (or re-verify with the smoke test below)

### Step 3: Apply Patch 1 — `getCodexAvailability` in `codex.mjs`

Find and replace the `getCodexAvailability` function body. The old code returns `available: false` when `app-server --help` fails:

**Old** (find this exact block):
```js
  const appServerStatus = binaryAvailable("codex", ["app-server", "--help"], { cwd });
  if (!appServerStatus.available) {
    return {
      available: false,
      detail: `${versionStatus.detail}; advanced runtime unavailable: ${appServerStatus.detail}`
    };
  }
```

**New** (replace with):
```js
  const appServerStatus = binaryAvailable("codex", ["app-server", "--help"], { cwd });
  if (!appServerStatus.available) {
    // Some internal distributions disable the `app-server` subcommand but still
    // support `review` natively.  Treat as available so native review can proceed.
    return {
      available: true,
      detail: `${versionStatus.detail}; app-server unavailable (internal distribution), native review only`
    };
  }
```

### Step 4: Apply Patch 2 — `getCodexLoginStatus` in `codex.mjs`

Find the tail of `getCodexLoginStatus`. The old code ends with:

**Old** (find this exact block — it's the final return of the function):
```js
  return {
    available: true,
    loggedIn: false,
    detail: result.stderr.trim() || result.stdout.trim() || "not authenticated"
  };
}
```

**New** (replace with — adds the fallback before the final return):
```js
  // Fallback: some internal distributions disable the `login` subcommand and use
  // SSO / internal auth instead.  If `login status` exits non-zero but the binary
  // is otherwise available, treat it as authenticated so review commands can run.
  const reviewHelp = runCommand("codex", ["review", "--help"], { cwd });
  if (!reviewHelp.error && reviewHelp.status === 0) {
    return {
      available: true,
      loggedIn: true,
      detail: "authenticated via internal distribution"
    };
  }

  return {
    available: true,
    loggedIn: false,
    detail: result.stderr.trim() || result.stdout.trim() || "not authenticated"
  };
}
```

**Important**: This replacement is inside `getCodexLoginStatus`. The closing `}` is the function's closing brace — make sure it matches uniquely. If the Edit tool reports ambiguity, add more surrounding context lines.

### Step 5: Apply Patch 3 — `executeReviewRun` in `codex-companion.mjs`

Find the native review dispatch inside `executeReviewRun`. The old code calls `runAppServerReview` directly:

**Old** (find this exact block):
```js
  if (reviewName === "Review") {
    const reviewTarget = validateNativeReviewRequest(target, focusText);
    const result = await runAppServerReview(request.cwd, {
      target: reviewTarget,
      model: request.model,
      onProgress: request.onProgress
    });
```

**New** (replace with — wraps in try/catch and adds CLI fallback):
```js
  if (reviewName === "Review") {
    const reviewTarget = validateNativeReviewRequest(target, focusText);
    let result;
    try {
      result = await runAppServerReview(request.cwd, {
        target: reviewTarget,
        model: request.model,
        onProgress: request.onProgress
      });
    } catch (appServerErr) {
      // Fallback: app-server is unavailable (e.g. internal distributions that
      // disable the subcommand).  Run `codex review --uncommitted` directly.
      const cliArgs = ["review"];
      if (reviewTarget?.type === "baseBranch" && reviewTarget.branch) {
        cliArgs.push("--base", reviewTarget.branch);
      } else {
        cliArgs.push("--uncommitted");
      }
      if (request.model) cliArgs.push("--model", request.model);

      result = await new Promise((resolve, reject) => {
        const proc = spawn("codex", cliArgs, {
          cwd: request.cwd,
          stdio: ["ignore", "pipe", "pipe"]
        });
        let stdout = "";
        let stderr = "";
        proc.stdout.on("data", (d) => { stdout += d.toString(); });
        proc.stderr.on("data", (d) => { stderr += d.toString(); });
        proc.on("close", (code) => {
          // Strip skill-loader error lines from stderr (cosmetic noise)
          const cleanStderr = stderr.split("\n").filter(l => !l.includes("codex_core_skills")).join("\n").trim();
          resolve({ status: code ?? 0, reviewText: stdout.trim(), reasoningSummary: null, threadId: null, sourceThreadId: null, turnId: null, stderr: cleanStderr });
        });
        proc.on("error", reject);
      });
    }
```

### Step 6: Smoke test

After applying all three patches, verify:

```bash
# Should print 2 (two occurrences of the internal distribution marker)
grep -c "internal distribution" ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/lib/codex.mjs

# Should print 1
grep -c "appServerErr" ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs

# Should print the login status as "authenticated via internal distribution"
node -e "
import('~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/lib/codex.mjs')
  .then(m => console.log(m.getCodexLoginStatus(process.cwd())))
" 2>/dev/null || echo "(ESM import test skipped — check via review run)"

# Quick functional test — should exit 0 and print review output
node ~/.claude-internal/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs review "" 2>&1 | head -5
```

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `"Codex CLI is not authenticated"` | Patch 1 or 2 missing | Re-apply Step 3 & 4 |
| `"Failed to parse codex app-server JSONL"` | Patch 3 missing | Re-apply Step 5 |
| `"Specify --uncommitted, --base..."` | `codex review` called without args | Check Patch 3 cliArgs logic |
| Edit tool reports "old_string not unique" | Plugin version changed the code | Read the file first, find the new location manually, adapt the old_string with more context |

## Notes

- These patches survive until the `openai-codex` plugin is updated (via `/plugins update` or reinstall)
- After any plugin update, run this skill again
- The patches only affect behavior when `app-server` / `login` subcommands are unavailable — on a standard codex install they are transparent no-ops
