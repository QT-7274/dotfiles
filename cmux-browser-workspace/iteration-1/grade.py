#!/usr/bin/env python3
"""Grade cmux-browser skill test assertions."""
import json
import os
from pathlib import Path

WORKSPACE = Path("/Users/shizheng/.skills-manager/skills/cmux-browser-workspace/iteration-1")

def grade_navigate(run_dir: Path) -> list:
    """Grade navigate-and-snapshot assertions."""
    results = []
    terminal = run_dir / "outputs/terminal_output.txt"
    title = run_dir / "outputs/title.txt"

    # page_opened
    val = terminal.exists() and "example.com" in terminal.read_text()
    results.append({"text": "page_opened", "passed": val, "evidence": "example.com in terminal output" if val else "missing"})

    # snapshot_taken
    val = terminal.exists() and "snapshot" in terminal.read_text()
    results.append({"text": "snapshot_taken", "passed": val, "evidence": "snapshot command found" if val else "missing"})

    # title_extracted
    val = title.exists() and "Example Domain" in title.read_text()
    results.append({"text": "title_extracted", "passed": val, "evidence": f"title={title.read_text().strip()[:50]}" if title.exists() else "file missing"})

    return results

def grade_form(run_dir: Path) -> list:
    """Grade form-interaction assertions."""
    results = []
    terminal = run_dir / "outputs/terminal_output.txt"
    screenshot = run_dir / "outputs/screenshot.png"

    # page_opened
    val = terminal.exists() and "httpbin.org" in terminal.read_text()
    results.append({"text": "page_opened", "passed": val, "evidence": "httpbin.org in terminal output" if val else "missing"})

    # form_filled
    txt = terminal.read_text() if terminal.exists() else ""
    val = "custname" in txt and "custemail" in txt
    results.append({"text": "form_filled", "passed": val, "evidence": "custname and custemail found in fill commands" if val else "missing"})

    # screenshot_saved
    val = screenshot.exists()
    results.append({"text": "screenshot_saved", "passed": val, "evidence": f"screenshot size={screenshot.stat().st_size} bytes" if val else "file missing"})

    return results

def grade_extract(run_dir: Path) -> list:
    """Grade extract-data assertions."""
    results = []
    terminal = run_dir / "outputs/terminal_output.txt"
    results_file = run_dir / "outputs/results.txt"

    # page_opened
    val = terminal.exists() and "news.ycombinator.com" in terminal.read_text()
    results.append({"text": "page_opened", "passed": val, "evidence": "news.ycombinator.com in terminal output" if val else "missing"})

    # url_and_title_got
    txt = results_file.read_text() if results_file.exists() else ""
    val = "news.ycombinator.com" in txt and "Hacker News" in txt
    results.append({"text": "url_and_title_got", "passed": val, "evidence": "URL and title found in results" if val else "missing"})

    # navigation_happened
    val = txt.count("news.ycombinator.com") >= 2 or "p=2" in txt or "p=3" in txt
    results.append({"text": "navigation_happened", "passed": val, "evidence": "multiple URLs or pagination found" if val else "missing"})

    return results

def main():
    all_grades = {}

    for eval_name, grader in [
        ("navigate-and-snapshot", grade_navigate),
        ("form-interaction", grade_form),
        ("extract-data", grade_extract),
    ]:
        for run_type in ["with_skill", "without_skill"]:
            run_dir = WORKSPACE / eval_name / run_type
            grades = grader(run_dir)
            passed = sum(1 for g in grades if g["passed"])
            total = len(grades)

            grading = {
                "eval_name": eval_name,
                "run_type": run_type,
                "pass_rate": passed / total if total else 0,
                "passed": passed,
                "total": total,
                "expectations": grades
            }

            out_path = run_dir / "grading.json"
            out_path.write_text(json.dumps(grading, indent=2, ensure_ascii=False))
            print(f"Graded {eval_name}/{run_type}: {passed}/{total} passed")
            all_grades[f"{eval_name}-{run_type}"] = grading

    # Summary
    print("\n=== SUMMARY ===")
    for key, g in all_grades.items():
        print(f"{key}: {g['passed']}/{g['total']} ({g['pass_rate']*100:.0f}%)")

if __name__ == "__main__":
    main()
