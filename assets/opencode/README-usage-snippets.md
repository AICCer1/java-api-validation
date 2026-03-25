# Usage snippets for OpenCode

## Copy into a project

```bash
mkdir -p .opencode/skills
mkdir -p .opencode/agents
mkdir -p .opencode/commands

cp -R /path/to/java-api-validation .opencode/skills/java-api-validation
cp /path/to/java-api-validation/assets/opencode/agents/api-validator.md .opencode/agents/api-validator.md
cp /path/to/java-api-validation/assets/opencode/commands/api-validate.md .opencode/commands/api-validate.md
```

## Invoke the subagent directly

```text
@api-validator validate user and auth endpoints against the dev server
```

## Invoke through the command

```text
/api-validate user and auth endpoints against the dev server
```
