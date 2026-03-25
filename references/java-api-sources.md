# Java API source discovery guide

Use this guide to find the API contract in a Java project before building curl cases.

## Preferred discovery order

### 1. OpenAPI / Swagger files

Look for:
- `openapi.yaml`
- `openapi.yml`
- `openapi.json`
- `swagger.yaml`
- `swagger.yml`
- `src/main/resources/openapi/*`
- `docs/openapi/*`

If an OpenAPI file exists and is current, prefer it as the contract source.

## 2. Spring controllers

Look for annotations such as:
- `@RestController`
- `@Controller`
- `@RequestMapping`
- `@GetMapping`
- `@PostMapping`
- `@PutMapping`
- `@DeleteMapping`
- `@PatchMapping`

Typical locations:
- `src/main/java/**/controller/**`
- `src/main/java/**/api/**`
- `src/main/java/**/web/**`

## 3. Request / response DTOs

Look for:
- `*Request.java`
- `*Response.java`
- `*DTO.java`
- `record` request/response types

Use these to infer field names, optionality, and payload shape.

## 4. Existing tests and examples

Useful sources:
- integration tests
- contract tests
- `.http` / `.rest` files
- Postman collections
- README examples

Typical paths:
- `src/test/java/**`
- `http/**`
- `docs/**`
- `postman/**`

## 5. Security and auth clues

Check for:
- Spring Security config
- JWT filters
- gateway config
- interceptor config
- `@PreAuthorize`
- auth examples in README or test fixtures

These often tell you which headers or tokens curl requests need.

## Practical extraction rule

When sources disagree, use this precedence unless the user says otherwise:
1. explicit design doc / OpenAPI spec
2. implemented controller mapping
3. tests/examples
4. DTO inference

Record source conflicts in the final Markdown report instead of silently picking one.
