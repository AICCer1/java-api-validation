# API Validation Report - spring-user-api-demo

- Generated at: 2026-03-25 10:35:00 UTC
- Base URL: `http://127.0.0.1:8080`
- Total cases: 5
- Passed: 4
- Failed: 1

## Summary

| Case | Method | Expected | Actual | Result |
|------|--------|----------|--------|--------|
| health-check | GET | 200 | 200 | PASS |
| list-users | GET | 200 | 200 | PASS |
| get-user-by-id | GET | 200, 404 | 200 | PASS |
| create-user | POST | 200, 201 | 201 | PASS |
| forbidden-without-token | GET | 401, 403 | 200 | FAIL |

## health-check

- Result: PASS
- Method: `GET`
- URL: `http://127.0.0.1:8080/actuator/health`
- Expected status: `[200]`
- Actual status: `200`
- Notes: Useful as the first smoke check before business endpoints

### Curl command

```bash
curl -sS -X GET http://127.0.0.1:8080/actuator/health -o /tmp/curl-suite/1-body.txt -D /tmp/curl-suite/1-headers.txt -w '%{http_code}' --max-time 30 -H 'Accept: application/json' -H 'Authorization: Bearer ***'
```

### Response headers

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

### Response body

```text
{"status":"UP"}
```

## list-users

- Result: PASS
- Method: `GET`
- URL: `http://127.0.0.1:8080/api/users?page=1&size=10`
- Expected status: `[200]`
- Actual status: `200`
- Notes: Requires the authenticated principal to have user-read permission

### Curl command

```bash
curl -sS -X GET 'http://127.0.0.1:8080/api/users?page=1&size=10' -o /tmp/curl-suite/2-body.txt -D /tmp/curl-suite/2-headers.txt -w '%{http_code}' --max-time 30 -H 'Accept: application/json' -H 'Authorization: Bearer ***'
```

### Response headers

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

### Response body

```text
{"total":1,"records":[{"id":1,"name":"Alice Skill Demo","email":"alice.skill.demo@example.com"}]}
```

## get-user-by-id

- Result: PASS
- Method: `GET`
- URL: `http://127.0.0.1:8080/api/users/1`
- Expected status: `[200, 404]`
- Actual status: `200`
- Notes: Use a seeded ID when available; 404 is acceptable on empty dev environments

### Curl command

```bash
curl -sS -X GET http://127.0.0.1:8080/api/users/1 -o /tmp/curl-suite/3-body.txt -D /tmp/curl-suite/3-headers.txt -w '%{http_code}' --max-time 30 -H 'Accept: application/json' -H 'Authorization: Bearer ***'
```

### Response headers

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

### Response body

```text
{"id":1,"name":"Alice Skill Demo","email":"alice.skill.demo@example.com","phone":"+8613800000000"}
```

## create-user

- Result: PASS
- Method: `POST`
- URL: `http://127.0.0.1:8080/api/users`
- Expected status: `[200, 201]`
- Actual status: `201`
- Notes: Adjust required fields to match the controller or OpenAPI schema

### Curl command

```bash
curl -sS -X POST http://127.0.0.1:8080/api/users -o /tmp/curl-suite/4-body.txt -D /tmp/curl-suite/4-headers.txt -w '%{http_code}' --max-time 30 -H 'Accept: application/json' -H 'Authorization: Bearer ***' -H 'Content-Type: application/json' --data-binary '{"name":"Alice Skill Demo","email":"alice.skill.demo@example.com","phone":"+8613800000000"}'
```

### Response headers

```text
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/users/42
```

### Response body

```text
{"id":42,"name":"Alice Skill Demo","email":"alice.skill.demo@example.com","phone":"+8613800000000"}
```

## forbidden-without-token

- Result: FAIL
- Method: `GET`
- URL: `http://127.0.0.1:8080/api/admin/users`
- Expected status: `[401, 403]`
- Actual status: `200`
- Notes: Intentional negative case to verify auth enforcement

### Curl command

```bash
curl -sS -X GET http://127.0.0.1:8080/api/admin/users -o /tmp/curl-suite/5-body.txt -D /tmp/curl-suite/5-headers.txt -w '%{http_code}' --max-time 30 -H 'Accept: application/json' -H 'Authorization: '
```

### Response headers

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

### Response body

```text
{"total":3,"records":[{"id":1,"name":"admin-visible-record"}]}
```

## Conclusion

- The API smoke path is healthy.
- Core user query and create flows behave as expected.
- The negative auth case failed because `/api/admin/users` still returned `200` without a token.
- This should be treated as an auth enforcement bug or a mismatch between implementation and design.
