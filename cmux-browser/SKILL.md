---
name: cmux-browser
description: Browser automation via cmux built-in browser commands. Use when the user needs to interact with websites through cmux's embedded browser surface, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task within the cmux environment. Triggers include requests to "open a website in cmux", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction inside cmux. Prefer cmux-browser over agent-browser when the user is already using cmux and wants browser automation within the cmux window (browser split), or when they want stable CSS-selector-based element targeting instead of @eN refs. Also triggers when the user mentions "cmux browser", "cmux 浏览器", or wants to use cmux's built-in webview automation.
allowed-tools: Bash(cmux browser:*)
hidden: true
---

# cmux-browser

Browser automation via cmux's built-in browser commands. The browser runs as an
embedded surface (split) inside the cmux window, not as a separate Chrome window.

No extra install needed — `cmux browser` is available wherever cmux is installed.

## Core differences from agent-browser

| | agent-browser | cmux-browser |
|---|---|---|
| Command prefix | `agent-browser` | `cmux browser` |
| Element refs | `@eN` (snapshot-generated) | CSS selectors (`#id`, `.class`, `button[type='submit']`) |
| Browser window | External Chrome window | Embedded split inside cmux |
| Install | `npm i -g agent-browser` | Built into cmux |
| Help system | `agent-browser skills get core` | `cmux browser --help` |
| Screenshot | `screenshot [path]` | `screenshot --out <path>` |
| Fill form | `fill @e1 "text"` | `fill "#id" --text "text"` |

## The core loop

```bash
# 1. Open a page (creates a new browser split in cmux)
cmux browser open "https://example.com"

# 2. Identify the browser surface (get surface ID like surface:2)
cmux browser identify

# 3. Wait for page load, then snapshot to discover elements
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
cmux browser surface:2 snapshot --interactive --compact

# 4. Act on elements via CSS selectors (discovered from snapshot)
cmux browser surface:2 click "button[type='submit']" --snapshot-after

# 5. Re-snapshot after any page change
cmux browser surface:2 snapshot --interactive
```

**Surface IDs** (e.g. `surface:2`) are persistent for a given browser split but
are assigned when the surface is created. Always run `identify` first if you
don't know the surface ID.

## Surface targeting

Most commands need a surface handle. Pass it as `--surface <id>` or as the
first positional argument after `browser`:

```bash
cmux browser surface:2 url
cmux browser --surface surface:2 url          # equivalent
```

Commands that don't need a surface: `open`, `open-split`, `new`, `identify`.

## Navigation

```bash
# Open in current workspace (default) or specific workspace/window
cmux browser open "https://example.com"
cmux browser open "https://example.com" --workspace workspace:3
cmux browser open "https://example.com" --window window:1
cmux browser open-split "https://news.ycombinator.com"
cmux browser surface:2 navigate "https://example.org/docs" --snapshot-after
cmux browser surface:2 back
cmux browser surface:2 forward
cmux browser surface:2 reload --snapshot-after
cmux browser surface:2 url
cmux browser surface:2 focus-webview
cmux browser surface:2 is-webview-focused
```

## Waiting

```bash
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
cmux browser surface:2 wait --selector "#checkout" --timeout-ms 10000
cmux browser surface:2 wait --text "Order confirmed"
cmux browser surface:2 wait --url-contains "/dashboard"
cmux browser surface:2 wait --function "window.__appReady === true"
```

## DOM interaction

All mutation commands support `--snapshot-after` for quick verification.

```bash
cmux browser surface:2 click "button[type='submit']" --snapshot-after
cmux browser surface:2 dblclick ".item-row"
cmux browser surface:2 hover "#menu"
cmux browser surface:2 focus "#email"
cmux browser surface:2 check "#terms"
cmux browser surface:2 uncheck "#newsletter"
cmux browser surface:2 scroll-into-view "#pricing"

# type supports both positional text and --text
cmux browser surface:2 type "#search" "cmux"
cmux browser surface:2 type "#search" --text "cmux"
cmux browser surface:2 fill "#email" --text "ops@example.com"
cmux browser surface:2 fill "#email" --text ""              # clear

# press/key/keydown/keyup are equivalent aliases
cmux browser surface:2 press Enter
cmux browser surface:2 key Enter
cmux browser surface:2 keydown Shift
cmux browser surface:2 keyup Shift

cmux browser surface:2 select "#region" --value "us-east"
cmux browser surface:2 scroll --dy 800 --snapshot-after
cmux browser surface:2 scroll --selector "#log-view" --dx 0 --dy 400
```

## Inspecting

```bash
cmux browser surface:2 snapshot --interactive --compact
cmux browser surface:2 snapshot --interactive --cursor    # include cursor position
cmux browser surface:2 snapshot --selector "main" --max-depth 5
cmux browser surface:2 screenshot --out /tmp/cmux-page.png

cmux browser surface:2 get title
cmux browser surface:2 get url
cmux browser surface:2 get text "h1"
cmux browser surface:2 get html "main"
cmux browser surface:2 get value "#email"
cmux browser surface:2 get attr "a.primary" --attr href
cmux browser surface:2 get count ".row"
cmux browser surface:2 get box "#checkout"
cmux browser surface:2 get styles "#total" --property color

cmux browser surface:2 is visible "#checkout"
cmux browser surface:2 is enabled "button[type='submit']"
cmux browser surface:2 is checked "#terms"

cmux browser surface:2 find role button --name "Continue"
cmux browser surface:2 find text "Order confirmed"
cmux browser surface:2 find label "Email"
cmux browser surface:2 find placeholder "Search"
cmux browser surface:2 find first ".row"
cmux browser surface:2 find last ".row"
cmux browser surface:2 find nth 2 ".row"

cmux browser surface:2 highlight "#checkout"
```

## JavaScript execution

```bash
cmux browser surface:2 eval "document.title"
cmux browser surface:2 addinitscript "window.__cmuxReady = true;"
cmux browser surface:2 addscript "document.querySelector('#name')?.focus()"
cmux browser surface:2 addstyle "#debug-banner { display: none !important; }"
```

## State (cookies, storage, session)

```bash
cmux browser surface:2 cookies get
cmux browser surface:2 cookies get --name session_id
cmux browser surface:2 cookies set session_id abc123 --domain example.com --path /
cmux browser surface:2 cookies clear --name session_id
cmux browser surface:2 cookies clear --all

cmux browser surface:2 storage local set theme dark
cmux browser surface:2 storage local get theme
cmux browser surface:2 storage session set flow onboarding
cmux browser surface:2 storage session get flow

cmux browser surface:2 state save /tmp/cmux-browser-state.json
cmux browser surface:2 state load /tmp/cmux-browser-state.json
```

## Tabs

```bash
cmux browser surface:2 tab list
cmux browser surface:2 tab new "https://example.com/pricing"
cmux browser surface:2 tab switch 1
cmux browser surface:2 tab close
cmux browser surface:2 tab close surface:7
```

## Download

```bash
# Trigger a download by clicking an element, then wait for it
cmux browser surface:2 click "a#download-report"
cmux browser surface:2 download --path /tmp/report.csv --timeout-ms 30000
```

## Browser settings

```bash
cmux browser surface:2 viewport 1920 1080
cmux browser surface:2 geolocation 37.7749 -122.4194
cmux browser surface:2 offline true
```

## Network

```bash
# Intercept and mock network requests
cmux browser surface:2 network route "**/api/data" --body '{"mock": true}'
cmux browser surface:2 network route "**/api/ads" --abort
cmux browser surface:2 network unroute "**/api/data"
cmux browser surface:2 network requests
```

## Recording

```bash
cmux browser surface:2 trace start /tmp/trace.json
cmux browser surface:2 trace stop /tmp/trace.json
cmux browser surface:2 screencast start
cmux browser surface:2 screencast stop
```

## Low-level input

```bash
cmux browser surface:2 input mouse move 100 200
cmux browser surface:2 input mouse down
cmux browser surface:2 input mouse up
cmux browser surface:2 input keyboard type "hello"
cmux browser surface:2 input touch tap 150 300
```

## Debugging

```bash
cmux browser surface:2 console list
cmux browser surface:2 console clear
cmux browser surface:2 errors list
cmux browser surface:2 errors clear
cmux browser surface:2 screenshot --out /tmp/cmux-failure.png
```

## Common patterns

### Login flow

```bash
cmux browser open "https://example.com/login"
cmux browser identify
# assume surface:2 was assigned
cmux browser surface:2 wait --load-state complete --timeout-ms 15000

# Always snapshot first to confirm actual element selectors
cmux browser surface:2 snapshot --interactive --compact

# Fill credentials (adjust selectors based on snapshot output)
cmux browser surface:2 fill "#email" --text "user@example.com"
cmux browser surface:2 fill "#password" --text "$PASSWORD"

# If button[type='submit'] fails, try snapshot again to find the correct selector
cmux browser surface:2 click "button[type='submit']" --snapshot-after
# Fallback if the above fails: cmux browser surface:2 click "button"

cmux browser surface:2 wait --url-contains "/dashboard"
cmux browser surface:2 screenshot --out ./login-success.png
```

### Find element when selector is uncertain

When you don't know the exact CSS selector, use `find` to locate by text,
role, label, placeholder, etc.:

```bash
cmux browser surface:2 find text "Sign in"
# Output: Found at selector button.btn-primary (index 0)
cmux browser surface:2 click "button.btn-primary"
```

**Warning:** `find text` can throw JavaScript exceptions on some sites
(e.g., Hacker News, SPAs with heavy JS). If `find` fails, immediately
fall back to `snapshot --interactive` to read the DOM and pick a selector
manually:

```bash
# If find fails...
cmux browser surface:2 find text "More"
# Error: js_error: JavaScript exception

# ...fall back to snapshot
cmux browser surface:2 snapshot --interactive --compact
# Read output: link "More" is at a.morelink
cmux browser surface:2 click "a.morelink"
```

### Persistent session

```bash
cmux browser surface:2 state save /tmp/session.json
# ... later ...
cmux browser surface:2 state load /tmp/session.json
cmux browser surface:2 reload
```

## Choosing selectors

Since cmux-browser uses CSS selectors (not @eN refs), prefer these strategies:

**Best practice: always snapshot first on an unfamiliar page.**

```bash
cmux browser surface:2 snapshot --interactive --compact
# Read the output to see actual element names and selectors, then act.
```

**Selector priority (most to least stable):**

1. **ID** — `#email`, `#submit-btn` (most stable)
2. **Attribute** — `input[type='email']`, `button[data-testid='login']`
3. **ARIA** — `[aria-label='Search']`, `[role='button']`
4. **Tag + partial class** — `button.btn-primary` (more stable than full hash class)
5. **Text via `find`** — use `find text "Submit"` to discover the selector, then use that selector directly. **Warning**: `find text` can throw JavaScript exceptions on some sites (e.g., Hacker News). If it fails, fall back to `snapshot --interactive`.
6. **Avoid class-only selectors** like `.css-1a2b3c` — they change on rebuild

**Common gotchas:**

- A `<button>` may not have `type="submit"` — check with snapshot first
- `input[type='text']` may actually be `input[type='']` or no type at all
- React/Vue generated class names change every build — don't rely on them
- `find` is for discovery, not production scripts — once you find the selector, hardcode it

If a selector fails, run `snapshot --interactive` to see the current DOM
structure and pick a better one.

## Troubleshooting

### Surface is reused instead of opening a new page

`cmux browser open` may reuse an existing browser surface if one already exists
in the workspace. If the initial URL is not what you expected, check for reuse:

```bash
cmux browser identify   # shows placement=reuse if surface was reused
cmux browser surface:2 url   # verify current URL
```

To force a fresh page, close existing browser surfaces first or use
`cmux browser open-split`.

### `find text` throws JavaScript exception

Some websites (e.g., Hacker News, SPAs) cause `find text` to fail with a
JS error. This is a cmux browser limitation, not a usage error. Workaround:

```bash
cmux browser surface:2 snapshot --interactive --compact
# Read the snapshot output, find the element's selector manually, then:
cmux browser surface:2 click "a.morelink"
```

### Selector not found (`not_found`)

The element exists but your selector does not match it. Common causes:

- Missing `type="submit"` on buttons — try `button` or `input[type='submit']`
- Shadow DOM — try `eval` with `document.querySelector` inside the shadow root
- iframe — use `cmux browser surface:2 frame "iframe[name='...']"` first
- Element not yet rendered — add a `wait --selector` before interacting

### Click succeeds but nothing happens

The element was found but the click did not trigger the expected action.
Try:

```bash
cmux browser surface:2 scroll-into-view "#submit"   # ensure visible
cmux browser surface:2 click "#submit" --snapshot-after   # verify page changed
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
```

If still no change, the element may need a real mouse event. Use low-level
input: `cmux browser surface:2 input mouse move 100 200 && input mouse down && input mouse up`.

### Screenshot is blank or wrong page

The browser surface may not be focused. Ensure the webview is active:

```bash
cmux browser surface:2 focus-webview
cmux browser surface:2 screenshot --out /tmp/page.png
```
