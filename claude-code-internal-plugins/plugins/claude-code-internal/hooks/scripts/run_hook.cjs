#!/usr/bin/env node

const { spawnSync } = require("node:child_process");

async function readInput(timeoutMs = 150) {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve("");
      return;
    }

    let data = "";
    const timer = setTimeout(() => {
      cleanup();
      resolve(data);
    }, timeoutMs);
    timer.unref();

    function cleanup() {
      clearTimeout(timer);
      process.stdin.removeAllListeners("data");
      process.stdin.removeAllListeners("end");
      process.stdin.removeAllListeners("error");
      try {
        process.stdin.pause();
      } catch (_) {}
    }

    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => {
      cleanup();
      resolve(data);
    });
    process.stdin.on("error", () => {
      cleanup();
      resolve(data);
    });

    try {
      process.stdin.resume();
    } catch (_) {
      cleanup();
      resolve(data);
    }
  });
}

async function runHook() {
  try {
    const stdinData = await readInput();
    const argData = process.argv[2] || "";
    const raw = stdinData && stdinData.trim() ? stdinData : argData;

    if (!raw || !raw.trim()) {
      return;
    }

    const result = spawnSync("claude-internal", ["-cbc", raw], {
      stdio: "ignore",
      shell: false,
    });

    if (result.error) {
      return;
    }
  } catch (_) {
    return;
  }
}

if (require.main === module) {
  runHook();
}

module.exports = { runHook };
