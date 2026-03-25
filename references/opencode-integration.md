# OpenCode integration notes

This skill is designed to live directly under one of these locations:
- `.opencode/skills/java-api-validation/`
- `.claude/skills/java-api-validation/`
- `.agents/skills/java-api-validation/`
- `~/.config/opencode/skills/java-api-validation/`

If this repository is cloned directly into one of those paths, OpenCode can discover it.

## Minimal custom command example

This repository already includes a ready-to-copy command file at:

- `assets/opencode/commands/api-validate.md`

Copy it to:

- `.opencode/commands/api-validate.md`

Then run:

```text
/api-validate user endpoints
```

The bundled command is configured to:
- use `api-validator`
- run as a subtask
- load the `java-api-validation` skill
- produce a Markdown verification report

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
