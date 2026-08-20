# Exercise 02 — Ground `/generate-response` with Order Data

## Goal

Extend the Day 1 response-generation feature so Claude can use verified order
information retrieved by the application.

## Time

Approximately 25 minutes.

## Starting point

You already have:

```text
POST /generate-response
ResponseService
ClaudeService
OrderRepository
GenerateResponseRequest / GenerateResponseResponse
```

The Day 1 endpoint can draft a response but cannot know verified order state.

## Requirement

Evolve `/generate-response` so that it can accept a customer/order reference,
retrieve the matching order through application code, and supply retrieved
order context to response generation.

The API response should make it possible to tell whether trusted order context
was actually used.

## Constraints

- Do not query MongoDB from `ClaudeService`.
- Do not give Claude direct database access.
- Do not trust an `order_id` without scoping it to the customer.
- Keep MongoDB access inside a repository.
- Keep response drafting inside the response-generation service layer.
- Do not invent order status when the lookup returns no authorized record.

## Test cases

Test:

1. a valid customer + order pair
2. the same order under a different customer
3. an order ID supplied without a customer ID

Record:

```text
case:
HTTP status:
trusted order context used?
what did the generated response claim?
```

## Deliverable

Explain which facts came from MongoDB, which text came from Claude, and which
decisions remained application-controlled.

## Answers

### Implementation

Built this once independently (route-level lookup + string-concatenated
prompt), then the instructor's own "Exercise 2 Sample Solution" landed in
a later pull touching the same files. Adopted theirs — same reasoning as
Exercise 06 on Day 1: staying on a parallel implementation just means
re-deriving every future exercise's starting point by hand. Final,
currently-live architecture:

- `app/schemas/ai.py` — `GenerateResponseRequest` gained optional
  `customer_id`/`order_id`, with a `@model_validator` rejecting `order_id`
  supplied without `customer_id`. `GenerateResponseResponse` gained
  `context_used: ResponseContextUsed` (`order_id: str | None`) so the
  caller can tell whether trusted context actually grounded the response.
- `app/services/generate_response_service.py` — new `GenerateResponseService`,
  a workflow layer that coordinates the order lookup and the draft
  generation, decoupling that orchestration from both the route and the
  low-level Claude call. Takes the whole `GenerateResponseRequest`,
  returns a `GenerateResponseResult` dataclass with `order_id_used`
  already resolved.
- `app/api/routes/ai.py` (`/generate-response`) — builds
  `GenerateResponseService(response_service=..., order_repository=...)`
  and delegates to it; the route itself no longer contains any lookup
  logic.
- `app/services/response_service.py` — `generate_draft` (renamed from
  `generate`) takes an optional `OrderContext` and builds a single
  structured payload — `{"customer_message": ..., "trusted_order_context":
  ...}` — serialized via `app/core/prompt_data.serialize_prompt_payload`
  into one clean JSON block sent to Claude. Cleaner than my original
  string-concatenation approach, and keeps the untrusted/trusted
  boundary explicit as a JSON key rather than prose framing.
- `ClaudeService` never touches MongoDB — `OrderRepository` is the only
  thing that does, called from `GenerateResponseService`, not the route
  or `ClaudeService`.

### Test cases

**Case 1 — valid customer + order pair**
```json
{"customer_message": "Whats the status of my order?", "customer_id": "CUST-101", "order_id": "ORD-1001"}
```
```text
HTTP status: 200
trusted order context used: yes (context_used.order_id = "ORD-1001")
what the response claimed: order ORD-1001, item "Wireless Mouse" (qty 1),
status "Delivered", delivered August 4 2026 11:15 AM, original estimated
delivery August 5 2026 — all values pulled directly from the OrderContext
MongoDB returned. Re-tested against the merged/final implementation
(input_tokens 338, output_tokens 165) — same facts, same guarantees, only
the prompt-construction and response wording changed.
```

**Case 2 — same order under a different customer**
```json
{"customer_message": "Whats the status of my order?", "customer_id": "CUST-102", "order_id": "ORD-1001"}
```
```text
HTTP status: 200
trusted order context used: no (context_used.order_id = null)
what the response claimed: nothing about order status — said it has no
verified order details for this account and asked the customer for more
information. ORD-1001 belongs to CUST-101, not CUST-102, so
get_order_for_customer returned None and no order facts were available
to state.
```

**Case 3 — order ID supplied without a customer ID**
```json
{"customer_message": "Whats the status of my order?", "order_id": "ORD-1001"}
```
```text
HTTP status: 422
trusted order context used: n/a — request never reached the route
what the response claimed: n/a — rejected by GenerateResponseRequest's
validator ("customer_id is required when order_id is provided") before
any Claude call or database query happened.
```

### Which facts came from where

- **MongoDB (via `OrderRepository`):** order existence, ownership
  (customer/order match), status, items, delivery dates — the only
  source of truth for anything order-specific.
- **Claude:** the wording of the draft reply, and the decision of what
  to say when no verified context is available (ask for more detail,
  don't guess). Claude never decides *whether* an order lookup happened
  or *what* the order's real status is — it only phrases what it was
  handed.
- **Application-controlled:** whether a lookup is attempted at all
  (only when both IDs are present), whether the customer/order pairing
  is authorized (the MongoDB query itself), what counts as "no
  authorized record" (`None`, not an error — same as Exercise 01), and
  `context_used` in the response, which is set from the repository's
  actual return value, never from what the request merely asked for.
  Case 2 is the clearest proof of the boundary: the request claimed
  ownership of ORD-1001, but the application's own database check
  overrode that claim and nothing about the order reached Claude at all.
