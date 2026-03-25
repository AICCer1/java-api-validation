# Case suite schema

Use this schema for `scripts/run_curl_suite.py`.

## Top-level shape

```json
{
  "suite_name": "user-api-validation",
  "base_url": "http://127.0.0.1:8080",
  "default_headers": {
    "Accept": "application/json"
  },
  "cases": []
}
```

## Supported top-level fields

- `suite_name`: human-readable suite name
- `base_url`: base URL for the target service
- `default_headers`: headers applied to every case unless overridden
- `cases`: list of request cases

Environment variables inside strings are supported through shell-style expansion, for example:

```json
{
  "base_url": "${API_BASE_URL}",
  "default_headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

## Case shape

```json
{
  "name": "get-user-by-id",
  "method": "GET",
  "path": "/api/users/1",
  "query": {
    "verbose": "true"
  },
  "headers": {
    "X-Trace-Id": "skill-demo"
  },
  "expected_status": [200],
  "timeout_seconds": 20,
  "notes": "Requires seeded user id=1"
}
```

## Supported case fields

- `name`: required; unique descriptive case name
- `method`: optional; defaults to `GET`
- `path`: required; request path, joined with `base_url`
- `query`: optional; object encoded as query string
- `headers`: optional; per-case headers overriding / extending `default_headers`
- `body`: optional; object, array, string, number, boolean, or null
- `body_file`: optional; path to a request body file used with `--data-binary @file`
- `expected_status`: optional; integer or list of integers, defaults to `[200]`
- `timeout_seconds`: optional; defaults to `30`
- `follow_redirects`: optional boolean; defaults to `false`
- `notes`: optional; recorded into the Markdown report

## Body rules

### JSON body

```json
{
  "name": "create-user",
  "method": "POST",
  "path": "/api/users",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "Alice",
    "email": "alice@example.com"
  },
  "expected_status": [200, 201]
}
```

If `body` is an object or array and `Content-Type` is missing, the runner will default to `application/json`.

### Raw string body

```json
{
  "name": "submit-raw-text",
  "method": "POST",
  "path": "/api/raw",
  "headers": {
    "Content-Type": "text/plain"
  },
  "body": "hello world",
  "expected_status": [202]
}
```

### File body

```json
{
  "name": "upload-payload",
  "method": "POST",
  "path": "/api/import",
  "headers": {
    "Content-Type": "application/json"
  },
  "body_file": "tmp/api-validation/import.json",
  "expected_status": [200, 202]
}
```

## Good case design rules

- Use concrete IDs that exist in the target environment
- Encode auth requirements explicitly in headers
- Prefer 1 endpoint behavior per case
- Record setup assumptions in `notes`
- Keep `expected_status` realistic; use multiple values only when the environment legitimately varies
