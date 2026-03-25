# OpenCode integration notes

This skill is designed to live directly under one of these locations:
- `.opencode/skills/java-api-validation/`
- `.claude/skills/java-api-validation/`
- `.agents/skills/java-api-validation/`
- `~/.config/opencode/skills/java-api-validation/`

If this repository is cloned directly into one of those paths, OpenCode can discover it.

## Minimal custom command example

Create `.opencode/commands/api-validate.md`:

```md
---
description: Validate Java APIs with curl and write a Markdown report
agent: build
---

Load the `java-api-validation` skill and validate the API described by $ARGUMENTS.

Required workflow:
1. use a subagent first to locate and normalize the contract source
2. create a JSON case suite
3. run the bundled curl validation script
4. write a Markdown report under docs/api-validation/
5. summarize pass/fail/blocked findings
```

Then run:

```text
/api-validate user endpoints
```

## Optional validation-focused subagent example

This repository already includes a ready-to-copy OpenCode subagent file at:

- `assets/opencode/agents/api-validator.md`

Copy it to:

- `.opencode/agents/api-validator.md`

Then invoke it in OpenCode with:

```text
@api-validator validate the user and auth endpoints against the current dev server
```

The bundled subagent is designed to:
- load `java-api-validation` first
- discover the best contract source
- build a curl case suite
- run `scripts/run_curl_suite.py`
- leave behind a Markdown report

## Practical use pattern

- main agent receives validation request
- main agent loads this skill
- main agent delegates discovery to `@explore` or `@general`
- main agent executes curl checks and writes report

This keeps discovery and execution separated and makes the validation phase more reproducible.
