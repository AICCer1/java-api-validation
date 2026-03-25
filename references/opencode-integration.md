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

Create `.opencode/agents/api-validator.md`:

```md
---
description: Validates Java HTTP APIs against design docs and running services
mode: subagent
model: anthropic/claude-sonnet-4-5
permission:
  bash:
    "*": ask
    "curl *": allow
  edit: allow
  read: allow
  write: allow
  grep: allow
  glob: allow
  list: allow
  skill:
    "java-api-validation": allow
---

Always load `java-api-validation` before starting validation work.
Prefer building a concrete curl case suite and a Markdown report instead of ad-hoc prose.
```

## Practical use pattern

- main agent receives validation request
- main agent loads this skill
- main agent delegates discovery to `@explore` or `@general`
- main agent executes curl checks and writes report

This keeps discovery and execution separated and makes the validation phase more reproducible.
