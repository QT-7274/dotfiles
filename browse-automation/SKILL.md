---
name: browse-automation
description: >
  Operate a persistent headless Chromium browser via the `browse` CLI for web automation,
  content extraction, scraping, and page interaction. Use this skill whenever you need to:
  open a webpage, take a screenshot, extract text/links/forms from a page, fill out forms,
  click buttons, scrape data, monitor page changes, run JavaScript in a browser context,
  inspect network requests or console logs, manage cookies, or automate any multi-step
  browser workflow. Also use when the user asks to "browse", "open a URL", "check a website",
  "screenshot a page", "scrape", "crawl", or interact with any web content that requires
  a real browser (not just HTTP fetch). This skill is the bridge between AI and the web -
  it gives you eyes and hands inside a real browser.
allowed-tools:
disable: false
---


# Browse — Persistent Headless Browser CLI

## What is browse?

`browse` is a CLI tool that runs a persistent Chromium browser in the background. You send
commands to navigate, interact, and extract data from web pages. The browser stays running
between commands (no startup cost after the first call), and sessions (cookies, storage,
open tabs) persist across restarts.

## How to invoke browse

`browse` is compiled and installed globally in PATH. Just run:

```bash
browse <command> [args...]
```

**Examples:**
```bash
browse goto "https://example.com"
browse screenshot --viewport                  # saved to project screenshots/ dir
browse snapshot -i
```

Do NOT `cd` into any specific directory or use `bun run dev` — just call `browse` directly.

## Architecture (why it matters to you)

browse uses a two-process model:

- **CLI process**: Your entry point. It's ephemeral — starts, sends a command, prints the result, exits.
- **Daemon process**: A long-lived HTTP server managing the Chromium instance. Starts automatically on first command, shuts down after 30 minutes of inactivity.

This means:
- The **first command** takes 2-3 seconds (starting Chromium). Subsequent commands are near-instant.
- State (cookies, localStorage, open tabs) **persists between commands** — you don't need to re-login each time.
- If something goes wrong, `browse stop` kills the daemon, and the next command auto-restarts it.

---

# Screenshot Directory

**IMPORTANT: Do NOT pass a file path to `screenshot`, `pdf`, or `responsive` commands.**
Just run `browse screenshot` or `browse screenshot --viewport` with no path argument.
Screenshots are automatically saved to the project's `screenshots/` directory
(configured by `browse.config.json`). The directory is auto-created. **No setup needed.**

```bash
# ✅ CORRECT — let browse pick the default path
browse screenshot                  # → <browse-project>/screenshots/browse-screenshot.png
browse screenshot --viewport       # → same, viewport only
browse pdf                         # → <browse-project>/screenshots/browse-page.pdf
browse responsive                  # → <browse-project>/screenshots/browse-responsive-{mobile,tablet,desktop}.png

# ❌ WRONG — do NOT hardcode /tmp/ paths
# browse screenshot /tmp/page.png        ← don't do this
# browse screenshot --viewport /tmp/x.png ← don't do this
```

The output always prints the full saved path — use that path with the Read tool to view the image.

The `screenshots/` dir is gitignored. To change the default location, edit `browse.config.json` in the project root:

```json
{
  "screenshotDir": "screenshots"
}
```

For one-off overrides, the `BROWSE_EXTRA_DIRS` env var still works (colon-separated paths).

---

# Command Reference

## 1. Navigation

```bash
browse goto <url>          # Open a URL (waits for DOM content loaded)
browse back                # Browser history back
browse forward             # Browser history forward
browse reload              # Reload current page
browse url                 # Print current URL
```

**Example — open a page and confirm:**
```bash
browse goto "https://example.com"
# → Navigated to https://example.com (200)
browse url
# → https://example.com
```

## 2. Content Extraction (Read Commands)

These commands extract data without modifying the page.

```bash
browse text                # Clean page text (scripts/styles stripped)
browse html [selector]     # innerHTML of selector, or full page HTML
browse links               # All links as "text → href"
browse forms               # Form fields as JSON (names, types, options)
browse accessibility       # Full ARIA accessibility tree
```

**Example — extract all links from a page:**
```bash
browse goto "https://news.ycombinator.com"
browse links
# → Show HN: ... → https://...
# → Ask HN: ... → https://...
```

**Example — inspect form structure before filling:**
```bash
browse goto "https://example.com/login"
browse forms
# → JSON with field names, types, placeholders, required flags
```

## 3. The Snapshot System (@refs)

This is the most powerful feature for interaction. Instead of writing fragile CSS selectors,
use `snapshot` to get a numbered reference map of page elements.

```bash
browse snapshot            # Full accessibility tree with @e1, @e2, ... refs
browse snapshot -i         # Interactive elements only (buttons, links, inputs)
browse snapshot -c         # Compact (skip empty structural nodes)
browse snapshot -d 2       # Limit tree depth to 2 levels
browse snapshot -s "nav"   # Scope to a CSS selector
browse snapshot -D         # Diff against previous snapshot (detect changes)
browse snapshot -a         # Annotated screenshot with red boxes on each ref
browse snapshot -C         # Find non-ARIA clickable elements (@c1, @c2, ...)
```

**Snapshot output looks like:**
```
@e1 [navigation] "Main"
  @e2 [link] "Home"
  @e3 [link] "About"
@e4 [heading] "Welcome" [level=1]
@e5 [textbox] "Email"
@e6 [textbox] "Password"
@e7 [button] "Sign In"
```

**Then use @refs in any command:**
```bash
browse fill @e5 "user@example.com"
browse fill @e6 "mypassword"
browse click @e7
```

### Snapshot best practices

- Always run `snapshot -i` before interacting with a page — it gives you the element map.
- Refs become **stale after navigation** (page change). Re-run `snapshot` after `goto`, `click` that triggers navigation, `back`, `forward`, or `reload`.
- Use `-D` (diff) to detect what changed on a page after an action.
- Use `-a` to get a visual map of where elements are (annotated screenshot saved to project `screenshots/` dir).
- `-C` finds elements that are clickable but not in the ARIA tree (custom divs with `cursor:pointer`, `onclick`, etc.). These get `@c` refs.

## 4. Interaction (Write Commands)

All interaction commands accept both CSS selectors and @refs.

```bash
browse click <sel|@ref>                 # Click element
browse fill <sel|@ref> <value>          # Clear and fill input field
browse select <sel|@ref> <value>        # Select dropdown option (by value, label, or text)
browse hover <sel|@ref>                 # Hover over element
browse type <text>                      # Type into currently focused element
browse press <key>                      # Press key: Enter, Tab, Escape, ArrowDown, etc.
browse scroll [sel|@ref]                # Scroll element into view, or scroll to page bottom
browse autoscroll [--max-steps N]       # Auto-scroll to load lazy content
browse wait <sel|@ref|--networkidle>    # Wait for element to appear or network to settle
browse upload <sel|@ref> <file> [...]   # Upload file(s) to file input
```

**Example — complete a search workflow:**
```bash
browse goto "https://www.google.com"
browse snapshot -i
# → @e1 [textbox] "Search"  @e2 [button] "Google Search"
browse fill @e1 "Claude AI"
browse press Enter
browse text
```

**Example — fill a multi-field form:**
```bash
browse goto "https://example.com/register"
browse snapshot -i
# → @e1 [textbox] "First Name"  @e2 [textbox] "Email"  @e3 [button] "Submit"
browse fill @e1 "John"
browse fill @e2 "john@example.com"
browse click @e3
```

**Autoscroll for infinite-scroll pages:**
```bash
browse goto "https://news.ycombinator.com"
browse autoscroll --max-steps 5 --delay 500
browse text
```

### Key interaction notes

- `fill` clears the field first, then types the value. Use `type` to append text without clearing.
- `click` on an `<option>` element is auto-routed to `select` — browse handles this for you.
- `press` supports modifier keys: `Shift+Enter`, `Control+a`, `Meta+c`.
- `wait --networkidle` is useful after actions that trigger API calls.

## 5. Inspection

```bash
browse js <expression>         # Run JS and return result (e.g., "document.title")
browse eval <file.js>          # Run JS file in page context (file must be in /tmp or cwd)
browse css <sel|@ref> <prop>   # Get computed CSS value
browse attrs <sel|@ref>        # Get all HTML attributes as JSON
browse is <prop> <sel|@ref>    # Check state: visible, hidden, enabled, disabled, checked, editable, focused
browse console [--errors]      # Console messages (--errors for errors/warnings only)
browse console --clear         # Clear console buffer
browse network [--clear]       # Network requests log
browse dialog [--clear]        # Dialog (alert/confirm/prompt) log
browse cookies                 # All cookies as JSON
browse storage [set k v]       # localStorage + sessionStorage (or set a value)
browse perf                    # Page load performance timings
```

**Example — check if an element is visible:**
```bash
browse is visible @e3
# → true
```

**Example — extract structured data with JS:**
```bash
browse js "JSON.stringify([...document.querySelectorAll('.price')].map(e => e.textContent))"
```

**Example — check for console errors after an action:**
```bash
browse click @e5
browse console --errors
# → (shows any JS errors that occurred)
```

## 6. Screenshots & Visual

Screenshots default to the project `screenshots/` directory (configured by `browse.config.json`).
**Never pass a path argument** — browse auto-saves to the right place.

```bash
browse screenshot                                 # Full-page → screenshots/browse-screenshot.png
browse screenshot --viewport                      # Viewport-only → screenshots/browse-screenshot.png
browse screenshot @e3                             # Element crop → screenshots/browse-screenshot.png
browse screenshot --clip 0,0,800,600              # Clip region → screenshots/browse-screenshot.png
browse pdf                                        # PDF → screenshots/browse-page.pdf
browse responsive                                 # 3 screenshots → screenshots/browse-responsive-{mobile,tablet,desktop}.png
```

**NEVER do this:**
```bash
# ❌ browse screenshot --viewport /tmp/page.png      ← don't pass a path
# ❌ browse screenshot /tmp/vandelaydesign.png        ← don't pass a path
```

**The `--viewport` flag is important** — without it, `screenshot` captures the full scrollable page.
When you just want what's visible on screen, always use `--viewport`.

**Example — take a screenshot and read it:**
```bash
browse goto "https://example.com"
browse screenshot --viewport
# Output prints: "Screenshot saved (viewport): /path/to/screenshots/browse-screenshot.png"
# Then use Read tool on that printed path to view the image
```

## 7. Multi-Tab Management

```bash
browse tabs                # List all open tabs (→ marks active tab)
browse tab <id>            # Switch to tab by ID
browse newtab [url]        # Open new tab (optionally navigate to URL)
browse closetab [id]       # Close tab (current if no ID given)
```

**Example — work with multiple pages:**
```bash
browse goto "https://page-a.com"
browse newtab "https://page-b.com"
browse tabs
# →   [1] Page A — https://page-a.com
# → → [2] Page B — https://page-b.com
browse tab 1               # Switch back to first tab
browse text                # Read content from Page A
```

## 8. Cookie & Session Management

```bash
browse cookie name=value                          # Set cookie on current domain
browse cookies                                    # View all cookies
browse cookie-import cookies.json                 # Import cookies from JSON file
browse cookie-import-browser chrome --domain x.com  # Import from installed Chrome
browse header Authorization:Bearer\ token123      # Set custom header
browse useragent "Mozilla/5.0 ..."                # Set user agent
```

**Cookie import is powerful for accessing authenticated pages** — export cookies from your
real browser and import them into browse to skip login flows.

## 9. Chain Commands (Multi-step Automation)

Execute multiple commands in sequence from a single call:

```bash
echo '[["goto","https://example.com"],["snapshot","-i"],["text"]]' | browse chain
```

Each command is `["command", "arg1", "arg2", ...]`. Results are returned with `[command]` prefixes.
Errors in one command don't stop the chain — subsequent commands still execute.

## 10. Handoff & Resume (Human-AI Collaboration)

When you're stuck (CAPTCHA, complex login, 2FA), hand control to the human:

```bash
browse handoff "Please complete the CAPTCHA"
# → Opens a visible Chrome window at the current page
# → User completes the manual step
browse resume
# → Returns to headless mode with a fresh snapshot
```

After 3 consecutive failures, browse suggests handoff automatically.

## 11. Server Control

```bash
browse status              # Health check + current URL + tab count
browse stop                # Shut down the daemon
browse restart             # Restart the daemon (clears all state)
```

## 12. Page Comparison

```bash
browse diff <url1> <url2>  # Unified text diff between two pages
```

---

# Recommended Workflows

## Workflow: Extract data from a page

```bash
browse goto "https://target-site.com"
browse snapshot -i                    # See what's on the page
browse text                           # Get all text content
# Or for structured data:
browse js "JSON.stringify([...document.querySelectorAll('table tr')].map(r => [...r.cells].map(c => c.textContent)))"
```

## Workflow: Fill and submit a form

```bash
browse goto "https://site.com/form"
browse snapshot -i                    # Get refs for form fields
browse fill @e1 "value1"
browse fill @e2 "value2"
browse select @e3 "Option B"         # For dropdowns
browse click @e4                      # Submit button
browse wait --networkidle             # Wait for response
browse text                           # Read result
```

## Workflow: Monitor a page for changes

```bash
browse goto "https://site.com/status"
browse snapshot                       # Baseline
# ... wait ...
browse reload
browse snapshot -D                    # Diff against baseline
```

## Workflow: Screenshot + visual inspection

```bash
browse goto "https://site.com"
browse screenshot --viewport
# Use Read tool to view the screenshot path from the output
# If you need to identify elements visually:
browse snapshot -a
# Read the annotated screenshot — shows red boxes with ref labels on each element
```

## Workflow: Authenticated session

```bash
# Option A: Import cookies from your real browser
browse cookie-import-browser chrome --domain github.com
browse goto "https://github.com/settings/profile"

# Option B: Login manually via handoff
browse goto "https://site.com/login"
browse handoff "Please log in"
# (user logs in in the visible browser)
browse resume
browse goto "https://site.com/dashboard"
browse text
```

---

# Troubleshooting

| Problem | Solution |
|---------|----------|
| "No active page" | Run `browse goto <url>` first |
| "Ref @eN not found" | Refs are stale — run `browse snapshot` again |
| "Element not found or not interactable" | The selector/ref doesn't match. Run `snapshot -i` to see available elements |
| "Path must be within..." | Default screenshots go to project `screenshots/`. Use `/tmp/` or cwd for other outputs. Or set `BROWSE_EXTRA_DIRS` env for custom dirs |
| Command hangs | The page might have a blocking dialog. Run `browse dialog` to check |
| Server won't start | Run `browse stop` then retry. Check `~/.browse/` for stale state |
| Need to reset everything | `rm -rf ~/.browse/` then run any command |
| `BROWSE_EXTRA_DIRS` not working | Ensure the directory exists, env var is exported, and daemon restarted (`browse stop`) |

# Key Reminders

1. **Always snapshot before interacting** — `snapshot -i` gives you the element map you need.
2. **Re-snapshot after navigation** — refs become stale when the page changes.
3. **NEVER pass file paths to screenshot/pdf/responsive** — just run `browse screenshot --viewport` with no path. Files auto-save to project `screenshots/`.
4. **Default screenshots land in project `screenshots/`** — configured by `browse.config.json`, auto-created, gitignored.
5. **The browser persists** — cookies, localStorage, tabs survive between commands.
6. **Use `--viewport` for screenshots** when you want just the visible area, not the full page scroll.
7. **Read screenshot files with the Read tool** — the command output prints the saved path, use that.
8. **If a path error occurs**, the error message tells you exactly which directories are allowed — check it.
