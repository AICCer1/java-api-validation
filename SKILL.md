---
name: java-api-validation
description: Validate Java backend APIs during the verification phase by extracting endpoint contracts from OpenAPI specs, Spring controllers, DTOs, or design docs, then running curl-based checks and writing a Markdown validation report. Use when OpenCode needs to verify designed or implemented HTTP APIs in Java/Spring projects, especially after API design, backend implementation, refactoring, or integration changes.
---

# Java API Validation

## Overview

Use this skill to turn Java API design or implementation artifacts into executable curl checks and a Markdown verification report.

Prefer this skill when the task is not “write unit tests”, but rather:
- verify designed endpoints against a running service
- confirm status codes, request/response shape, auth behavior, and obvious contract drift
- leave behind a human-readable verification report under the repository

## Core workflow

### 1. Locate the contract source

Prefer sources in this order:
1. OpenAPI / Swagger spec
2. design docs that define endpoints
3. Spring controllers and request/response DTOs
4. existing HTTP examples or integration tests

Read `references/java-api-sources.md` when source discovery is unclear.

### 2. Delegate contract extraction to a subagent

If subagents are available in OpenCode, delegate the contract-extraction pass first:
- Use `@explore` for read-only discovery of controllers, DTOs, and spec files
- Use `@general` when you want a synthesized endpoint list or a proposed case suite file

Have the subagent produce a concrete list of candidate validation cases, not prose.

Use `references/subagent-contract-extraction.md` for the expected output shape.

### 3. Build a case suite file

Create a JSON suite file that matches `references/case-schema.md`.

Prefer storing it under a temporary or traceable location such as:
- `tmp/api-validation/cases.json`
- `docs/api-validation/cases.json`
- `verification/api/cases.json`

Include only realistic cases that can actually be exercised against the target environment.

### 4. Confirm runtime prerequisites

Before executing curl checks, confirm:
- base URL
- auth token or cookie if required
- seeded IDs / fixture data needed by the test cases
- service is already running, or document how it was started

If any of these are missing and cannot be inferred safely, ask the user instead of guessing.

### 5. Run curl-based validation

Use the bundled script:

```bash
python3 scripts/run_curl_suite.py \
  --cases tmp/api-validation/cases.json \
  --report docs/api-validation/report.md
```

The script executes real `curl` commands, captures status code / headers / body, and writes a Markdown report.

### 6. Record results in Markdown

The report must include:
- suite metadata
- pass/fail summary
- exact curl command used for each case
- expected vs actual status
- response headers and response body preview
- blocked / setup issues when the environment is not ready

Do not hide infrastructure/setup failures. Mark them clearly as blocked or environment issues.

### 7. Finish with a validation conclusion

After the report is generated, summarize:
- passed cases
- failed cases
- blocked cases
- contract mismatches found
- whether the API is ready for the next phase

## Execution rules

### Prefer real HTTP verification over code-only guessing

If a runnable service exists, actually execute curl checks. Do not stop at static analysis unless the environment makes execution impossible.

### Keep the case suite concrete

Each case should describe a real request the runtime can execute. Avoid vague cases like “check login works”.

### Separate contract issues from environment issues

Examples of environment issues:
- app is not running
- token missing
- seed data missing
- endpoint only exists in design but not deployed

Examples of contract issues:
- wrong status code
- missing field
- unexpected field type
- auth behavior differs from spec

### Write reports to the repository

Prefer report paths such as:
- `docs/api-validation/report.md`
- `docs/verification/api-validation-YYYY-MM-DD.md`
- `tmp/api-validation/report.md`

If the project already has a verification/reports convention, follow it.

## Use the bundled resources

### `scripts/run_curl_suite.py`

Run a JSON case suite through real `curl` commands and emit a Markdown report.

Use this script for deterministic execution instead of hand-writing one-off curl commands when there are multiple endpoints to validate.

### `references/case-schema.md`

Read this before creating the suite JSON file.

### `references/java-api-sources.md`

Read this when you need to discover where the API contract lives in a Java/Spring project.

### `references/subagent-contract-extraction.md`

Read this when delegating the contract-extraction step to `@explore` or `@general`.

### `references/opencode-integration.md`

Read this when wiring the skill into OpenCode commands or validation-stage agents.

### `assets/opencode/agents/api-validator.md`

Copy this file into `.opencode/agents/api-validator.md` when you want a ready-made validation subagent that can be invoked with `@api-validator`.

## Recommended working pattern in OpenCode

When the request is “validate the API we designed/implemented”, use this sequence:

1. Load this skill
2. Use a subagent to locate and normalize the contract source
3. Create `cases.json`
4. Run `scripts/run_curl_suite.py`
5. Review the generated Markdown report
6. Summarize the outcome and next actions

## What not to do

- Do not claim validation passed without running curl when a runnable environment exists
- Do not bury failed cases inside prose without a structured report
- Do not invent auth headers, IDs, or request bodies if the project does not define them
- Do not silently rewrite the contract source; treat design docs/spec/controllers as the source of truth for validation
