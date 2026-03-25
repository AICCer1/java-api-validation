# Subagent contract extraction pattern

Use a subagent first when the API contract is spread across controllers, DTOs, docs, and examples.

## Recommended choices

### Use `@explore`

Use `@explore` when you want a read-only discovery pass:
- find OpenAPI files
- list controller files
- identify DTOs
- locate auth and test examples

Expected output:
- source file paths
- endpoint inventory
- auth clues
- unresolved gaps

### Use `@general`

Use `@general` when you want a synthesized case proposal:
- normalize endpoint list
- suggest concrete curl cases
- draft a `cases.json` file shape

Expected output:
- machine-friendly candidate suite
- clear environment assumptions
- noted ambiguities

## Prompt template for subagent

Use a prompt close to this:

```text
Analyze this Java project for API validation.

Goal:
- identify the most reliable API contract source
- extract concrete endpoints suitable for curl validation
- propose a JSON case suite compatible with references/case-schema.md

Return:
1. contract source files
2. endpoint list
3. auth/runtime assumptions
4. candidate cases in JSON form
5. unresolved questions
```

## What the parent agent should do after the subagent returns

1. Review whether the proposed cases are executable in the actual environment
2. Fill in base URL, auth headers, and seeded IDs if missing
3. Save the final `cases.json`
4. Run `scripts/run_curl_suite.py`
5. Write or refine the Markdown report
