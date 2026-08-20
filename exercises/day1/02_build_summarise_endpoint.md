# Exercise 02 — Build the First Claude-Backed Endpoint

## Goal

Create a small FastAPI endpoint that calls Claude through the provided application service boundary.

## Time

Approximately 30 minutes.

## Requirement

Build:

```text
POST /summarise
```

The endpoint receives customer-support text and returns a concise summary.

The response must also expose basic Claude usage information so the caller can see which model was used and the input/output token counts.

## Constraints

- Use the existing `ClaudeService`.
- Do not put the Anthropic API key in source code.
- Do not create a new Anthropic client directly inside the route.
- Validate the input length.
- Return an explicit response model rather than the raw Anthropic SDK response.
- Keep the summary use case separate from the low-level Claude client.

## Test message

Use a realistic support complaint of at least a few sentences.

## Deliverable

A working request in Postman and a short explanation of:

```text
HTTP route
    ->
application code
    ->
ClaudeService
    ->
Claude
    ->
response model
```

After the endpoint works, test a substantially longer complaint and compare the input/output token counts with your first request.

## Answers

### Files added / updated

```text
app/schemas/summarise.py        SummariseRequest, SummariseResponse
app/prompts/summarise.py        system prompt text
app/services/summarise_service.py   SummariseService (the "summary use case")
app/core/dependencies.py        get_claude_service() cached singleton
app/api/routes/summarise.py     POST /summarise route
app/api/router.py               updated: registers summarise_router
.env                             CLAUDE_MODEL set; ANTHROPIC_API_KEY filled locally, not committed
```

### Constraint -> where satisfied

- Use existing `ClaudeService` -> `SummariseService` calls `claude_service.generate_text(...)`, never touches `AsyncAnthropic`.
- No API key in source -> key lives only in `.env` (gitignored), read via `app/config.py` `Settings`.
- No new Anthropic client inside route -> route takes `ClaudeService` via `Depends(get_claude_service)`, client built once in `app/core/dependencies.py`.
- Validate input length -> `SummariseRequest.text: str = Field(min_length=1, max_length=5000)`.
- Explicit response model -> `SummariseResponse` (summary, model, input_tokens, output_tokens), not raw `message` object.
- Summary use case separate from low-level client -> `SummariseService` (business logic: prompt + shaping response) vs `ClaudeService` (generic Claude I/O only).

### Request flow

```text
HTTP route              app/api/routes/summarise.py       receives SummariseRequest
    ->
application code        app/services/summarise_service.py  SummariseService.summarise(text)
    ->
ClaudeService            app/services/claude_service.py     generate_text(text, system=..., max_tokens=200)
    ->
Claude                   Anthropic messages API              returns text + usage
    ->
response model           app/schemas/summarise.py            SummariseResponse returned to caller
```

### Test results

Short complaint (~35 words):
```text
input_tokens: 94
output_tokens: 170
```

Longer complaint (~200 words):
```text
input_tokens: 378
output_tokens: 197
```

Observation: input_tokens scaled roughly 4x with the ~4x increase in source text length (94 -> 378), confirming input cost tracks what you send. output_tokens stayed close (170 -> 197) despite the much longer input, bounded by `max_tokens=200` — output size is capped by the model's stopping behaviour, not driven proportionally by input length.

Note: system prompt was overwritten by an upstream pull mid-exercise (course repo pushed its own minimal version to `app/prompts/summarise.py`); these numbers were produced with that minimal prompt, not the original 3-sentence "don't invent" version first written for this exercise.
