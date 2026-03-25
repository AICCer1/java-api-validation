---
description: Validate Java APIs with curl and write a Markdown verification report
agent: api-validator
subtask: true
---

Load the `java-api-validation` skill and validate the Java API scope described below.

Validation target:
$ARGUMENTS

Required workflow:
1. identify the best contract source from OpenAPI, design docs, Spring controllers, DTOs, tests, or HTTP examples
2. build a concrete JSON case suite compatible with the skill schema
3. confirm runtime prerequisites such as base URL, auth, and seed data assumptions
4. run curl-based validation using the bundled runner when available
5. write a Markdown report under `docs/api-validation/` or `tmp/api-validation/`
6. summarize passed, failed, and blocked cases with contract mismatches and next actions

Do not stop at static analysis if a runnable environment exists.
Do not claim success without running real HTTP checks.
