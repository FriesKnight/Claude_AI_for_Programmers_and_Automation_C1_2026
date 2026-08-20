# Exercise 06 — Build a Customer Response Endpoint

## Goal

Build a second AI-powered backend use case while preserving the application's service boundaries.

## Time

Approximately 35–40 minutes.

## Requirement

Create:

```text
POST /generate-response
```

The endpoint receives a customer-support message and returns a draft response suitable for sending to the customer.

Return basic model/token usage with the draft.

## Important limitation

Day 1 has no trusted order or FAQ database integration yet.

The generated response must therefore avoid claiming private or business facts that the application has not supplied.

## Constraints

- Reuse `ClaudeService`.
- Keep the response-generation prompt outside the FastAPI route.
- Use an application service for the response-generation use case.
- Validate request and response data with Pydantic.
- Do not invent order status, refund status, account data, or company policy.
- Do not add MongoDB in this exercise.

## Test

Try at least two different support messages.

For each, ask:

> What facts did the backend genuinely know?

## Deliverable

A working Postman request and a short explanation of why the endpoint cannot yet give verified order-specific answers.

If you finish early, write down what trusted data you would want to retrieve on Day 2.

## Answers

### Implementation

Added, mirroring the existing `/analyse` boundary pattern:

- `app/prompts/generate_response.py` — `GENERATE_RESPONSE_SYSTEM_PROMPT`,
  outside the route, with hard rules against stating order/refund/account/
  payment status, claiming a lookup or action already happened, or quoting
  policy/warranty terms the app never supplied.
- `app/schemas/ai.py` — `GenerateResponseRequest` (`message`, 5–5000 chars)
  and `GenerateResponseResponse` (`draft_response` + `AIUsage`), both
  `StrictModel` (extra fields forbidden).
- `app/services/response_service.py` — `ResponseService`, reuses
  `ClaudeService.generate_text` (unstructured — a draft reply is prose,
  not a schema like `TicketAnalysis`).
- `app/api/routes/ai.py` — `POST /generate-response`, same shape as
  `/analyse`: build `ClaudeService`, run the service call in a
  `try/finally`, close the client, return the validated response model.

No MongoDB, no persistence — response is generated and returned, nothing
stored.

### Test 1 — Postman request

```text
POST http://127.0.0.1:8000/generate-response
Content-Type: application/json

{
  "message": "My order #4471 was supposed to arrive 3 days ago and I still have nothing. I paid extra for expedited shipping. This is really frustrating."
}
```

Response:

```json
{
  "draft_response": "Thank you for reaching out, and I completely understand how frustrating this must be, especially after paying extra for expedited shipping. I'm sorry for the inconvenience this has caused.\n\nI want to make sure your order #4471 is properly looked into, so our team will review the details and shipping information on your account. Once we have more information, we will follow up with you to help resolve this as quickly as possible. Thank you for your patience while we look into this.",
  "usage": {
    "model": "claude-sonnet-5",
    "input_tokens": 368,
    "output_tokens": 138
  }
}
```

**What facts did the backend genuinely know?** Only the order number the
customer typed (#4471) and the words of their message. Nothing about
whether that order exists, its actual shipping status, or expedited-
shipping eligibility. The draft correctly avoids claiming any of that —
it says the team "will review," never "your package is delayed due to X"
or "you'll be refunded the expedited fee."

### Test 2 — Postman request

```text
POST http://127.0.0.1:8000/generate-response
Content-Type: application/json

{
  "message": "Can I get a refund for the jacket I returned last week? Also does it come with a warranty?"
}
```

Response:

```json
{
  "draft_response": "Thank you for reaching out, and I understand you're looking for clarity on both your return and warranty questions. I want to make sure you get accurate information, so our team will look into the status of your returned jacket and confirm the applicable warranty details for your purchase. Please expect a follow-up with specifics once that review is complete, and thank you for your patience in the meantime.",
  "usage": {
    "model": "claude-sonnet-5",
    "input_tokens": 348,
    "output_tokens": 115
  }
}
```

**What facts did the backend genuinely know?** Nothing beyond the message
text — no record of the return, no refund status, no warranty terms. The
draft deliberately stays silent on refund amount, refund timeline, and
warranty length/coverage, and instead defers to "team will look into it
and confirm" — exactly the boundary the exercise asks for.

### Why it can't yet give verified order-specific answers

There's no database or order/FAQ system wired in on Day 1 — `ClaudeService`
only ever sees the raw message text passed to it. The model has no way to
know if order #4471 is real, what its status is, or what the return/
warranty policy actually says, so the only honest response is one that
acknowledges the issue and defers specifics to a follow-up, which is what
the system prompt enforces.

### Comparing to the instructor's official solution

The instructor's own solution landed later in the repo history
(`8d4bd1e`, "Added POST /generate-response endpoint (Exercise 6 Solution)"),
alongside the Day 2 database scaffolding. Kept my implementation above as
the answer since it was already built and tested independently, but here's
the diff:

|                         | Mine | Instructor's |
|-------------------------|------|---------------|
| Request field           | `message` | `customer_message` |
| Response length limit   | none | `draft_response` capped at 1-5000 chars via `Field` |
| Prompt module            | `app/prompts/generate_response.py` | `app/prompts/response_generation.py` |
| System prompt name       | `GENERATE_RESPONSE_SYSTEM_PROMPT` | `RESPONSE_GENERATION_SYSTEM_PROMPT` |
| Service method            | `generate_response()` | `generate()` |
| User prompt shaping       | prefixes with `"Customer support message:\n"` before sending to Claude | passes `customer_message` straight through, no framing text |

Functionally near-identical — same hard rules (no invented order/refund/
account/policy facts, no claiming an action already happened), same
`ClaudeService.generate_text` call with `max_tokens=300`, same response
shape (`draft_response` + `AIUsage`). Two differences worth noting:

- The instructor's version bounds `draft_response` length with a Pydantic
  `Field`; mine doesn't — a genuine gap, since nothing currently stops an
  unexpectedly long completion from passing through unbounded. Worth
  adding `Field(min_length=1, max_length=5000)` to `GenerateResponseResponse.draft_response`.
- Mine wraps the raw message with `"Customer support message:\n"` before
  it reaches Claude; the instructor's sends the customer's text unframed.
  Wrapping it makes the boundary between instruction and data slightly
  more explicit to the model (similar reasoning to the prompt-injection
  guard added to `SUMMARISE_SYSTEM_PROMPT` in Exercise 03) — a small
  defensive habit worth keeping even though the underlying request/
  response contract is otherwise the same.

### Day 2 wishlist

Trusted data worth retrieving before generating a response:
- order record (status, items, shipping method, expected delivery date)
  keyed off an order number extracted from the message
- return/refund record tied to the customer or order
- approved FAQ/policy snippets (warranty length, return window) fetched
  by topic instead of left to the model to guess or omit
- customer identity/account lookup, so the review flag can also carry
  enough context for the human reviewer.

### Update — live code now matches the instructor's schema

When merging the instructor's Day 2 pushes, Exercise 2
(`exercises/day2/02_ground_generate_response.md`) turned out to build
directly on their original `customer_message`/`response_generation.py`
structure, adding `customer_id`, `order_id`, and a `context_used` field
to `GenerateResponseResponse`. Kept diverging from that would mean
rebuilding their grounding exercise on a different schema by hand, so
the live code (`app/schemas/ai.py`, `app/services/response_service.py`,
`app/api/routes/ai.py`) was updated to adopt their `customer_message`
version instead of the `message` version documented above.

The write-up and test results above are left as-is — they're an accurate
record of what was actually built and tested for this exercise. The
route currently returns `context_used: {"order_id": null}` since no
trusted order/FAQ lookup is wired in yet; that's Exercise 2's job.
