#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode


def expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    return value


def normalize_expected_status(value: Any) -> List[int]:
    if value is None:
        return [200]
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        return [int(v) for v in value]
    raise ValueError(f"Unsupported expected_status: {value!r}")


def build_url(base_url: str, case: Dict[str, Any]) -> str:
    path = case.get("path")
    if not path:
        raise ValueError(f"Case {case.get('name', '<unnamed>')} missing path")
    if path.startswith("http://") or path.startswith("https://"):
        url = path
    else:
        url = base_url.rstrip("/") + "/" + str(path).lstrip("/")

    query = case.get("query") or {}
    if query:
        query_str = urlencode(query, doseq=True)
        sep = "&" if "?" in url else "?"
        url = url + sep + query_str
    return url


def render_body(case: Dict[str, Any], headers: Dict[str, str]):
    body = case.get("body", None)
    body_file = case.get("body_file")
    if body is not None and body_file:
        raise ValueError(f"Case {case.get('name', '<unnamed>')} cannot set both body and body_file")

    if body_file:
        return f"@{body_file}", headers

    if body is None:
        return None, headers

    if isinstance(body, (dict, list)):
        if not any(k.lower() == "content-type" for k in headers):
            headers["Content-Type"] = "application/json"
        return json.dumps(body, ensure_ascii=False), headers

    return str(body), headers


def build_curl_args(base_url: str, default_headers: Dict[str, str], case: Dict[str, Any],
                    body_path: Path, header_path: Path) -> List[str]:
    method = str(case.get("method", "GET")).upper()
    url = build_url(base_url, case)
    headers = dict(default_headers)
    headers.update(case.get("headers") or {})
    headers = {str(k): str(v) for k, v in expand_env(headers).items()}
    data_arg, headers = render_body(expand_env(case), headers)
    timeout_seconds = int(case.get("timeout_seconds", 30))
    follow_redirects = bool(case.get("follow_redirects", False))

    args = [
        "curl",
        "-sS",
        "-X",
        method,
        url,
        "-o",
        str(body_path),
        "-D",
        str(header_path),
        "-w",
        "%{http_code}",
        "--max-time",
        str(timeout_seconds),
    ]

    if follow_redirects:
        args.append("-L")

    for key, value in headers.items():
        args.extend(["-H", f"{key}: {value}"])

    if data_arg is not None:
        args.extend(["--data-binary", data_arg])

    return args


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n...[truncated to {max_chars} chars]"


def write_report(report_path: Path, suite: Dict[str, Any], results: List[Dict[str, Any]], max_body_chars: int) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: List[str] = []
    lines.append(f"# API Validation Report - {suite.get('suite_name', 'unnamed-suite')}")
    lines.append("")
    lines.append(f"- Generated at: {timestamp}")
    lines.append(f"- Base URL: `{suite.get('base_url', '')}`")
    lines.append(f"- Total cases: {total}")
    lines.append(f"- Passed: {passed}")
    lines.append(f"- Failed: {failed}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Case | Method | Expected | Actual | Result |")
    lines.append("|------|--------|----------|--------|--------|")
    for r in results:
        lines.append(
            f"| {r['name']} | {r['method']} | {', '.join(map(str, r['expected_status']))} | {r['http_status']} | {'PASS' if r['passed'] else 'FAIL'} |"
        )
    lines.append("")

    for r in results:
        lines.append(f"## {r['name']}")
        lines.append("")
        lines.append(f"- Result: {'PASS' if r['passed'] else 'FAIL'}")
        lines.append(f"- Method: `{r['method']}`")
        lines.append(f"- URL: `{r['url']}`")
        lines.append(f"- Expected status: `{r['expected_status']}`")
        lines.append(f"- Actual status: `{r['http_status']}`")
        if r.get("notes"):
            lines.append(f"- Notes: {r['notes']}")
        if r.get("curl_exit_code") not in (None, 0):
            lines.append(f"- curl exit code: `{r['curl_exit_code']}`")
        lines.append("")
        lines.append("### Curl command")
        lines.append("")
        lines.append("```bash")
        lines.append(r["curl_command"])
        lines.append("```")
        lines.append("")
        if r.get("stderr"):
            lines.append("### curl stderr")
            lines.append("")
            lines.append("```text")
            lines.append(trim_text(r["stderr"], max_body_chars))
            lines.append("```")
            lines.append("")
        lines.append("### Response headers")
        lines.append("")
        lines.append("```text")
        lines.append(trim_text(r["response_headers"], max_body_chars))
        lines.append("```")
        lines.append("")
        lines.append("### Response body")
        lines.append("")
        lines.append("```text")
        lines.append(trim_text(r["response_body"], max_body_chars))
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def run_suite(cases_path: Path, report_path: Path, max_body_chars: int) -> int:
    suite = expand_env(json.loads(cases_path.read_text(encoding="utf-8")))
    base_url = suite.get("base_url")
    if not base_url:
        raise ValueError("Suite missing base_url")

    default_headers = suite.get("default_headers") or {}
    cases = suite.get("cases") or []
    if not cases:
        raise ValueError("Suite contains no cases")

    results: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="curl-suite-") as tmp:
        tmpdir = Path(tmp)
        for idx, case in enumerate(cases, start=1):
            case = expand_env(case)
            name = case.get("name") or f"case-{idx}"
            body_path = tmpdir / f"{idx}-body.txt"
            header_path = tmpdir / f"{idx}-headers.txt"
            curl_args = build_curl_args(base_url, default_headers, case, body_path, header_path)
            proc = subprocess.run(curl_args, text=True, capture_output=True)
            http_code = proc.stdout.strip() or "000"
            expected_status = normalize_expected_status(case.get("expected_status"))
            passed = proc.returncode == 0 and http_code.isdigit() and int(http_code) in expected_status
            results.append({
                "name": name,
                "method": str(case.get("method", "GET")).upper(),
                "url": build_url(base_url, case),
                "expected_status": expected_status,
                "http_status": http_code,
                "passed": passed,
                "notes": case.get("notes", ""),
                "curl_exit_code": proc.returncode,
                "curl_command": shlex.join(curl_args),
                "stderr": proc.stderr,
                "response_headers": read_text(header_path),
                "response_body": read_text(body_path),
            })

    write_report(report_path, suite, results, max_body_chars)
    return 0 if all(r["passed"] for r in results) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run curl-based API validation and write a Markdown report")
    parser.add_argument("--cases", required=True, help="Path to the JSON case suite")
    parser.add_argument("--report", required=True, help="Path to the Markdown report to write")
    parser.add_argument("--max-body-chars", type=int, default=4000, help="Maximum chars to keep per response block")
    args = parser.parse_args()

    cases_path = Path(args.cases)
    report_path = Path(args.report)
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases file not found: {cases_path}")

    return run_suite(cases_path, report_path, args.max_body_chars)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"run_curl_suite.py error: {exc}", file=sys.stderr)
        sys.exit(2)
