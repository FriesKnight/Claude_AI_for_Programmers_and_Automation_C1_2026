# Exercise 05 — Structured Analysis Challenge

## Goal

Test a structured AI endpoint and distinguish AI judgement from application contract.

## Time

Approximately 25 minutes.

## Starting point

The application exposes:

```text
POST /analyse
```

## Step 1 — Predict before running

Your group will receive a support message.

Before sending it, predict the likely:

```text
category
sentiment
priority
whether an order lookup may be required
whether policy/FAQ information may be required
whether human review may be required
```

Record your prediction.

## Step 2 — Run the request

Send the message to `/analyse`.

Record the structured result and token usage.

## Step 3 — Compare

Discuss:

1. Which parts matched your prediction?
2. Which parts differed?
3. Did the response keep the same schema as other groups?
4. Which values are constrained by the application?
5. Which values remain AI judgement?

## Step 4 — Validation check

Create one Python dictionary that is syntactically valid data but does **not** satisfy the application's analysis contract.

Use the application's Pydantic model to confirm that validation rejects it.

## Deliverable

Be prepared to show:

```text
prediction
actual result
one invalid object
validation result
```

Do not change the allowed enums just to make your invalid object pass.

## Answers

### Test message

```text
I was charged twice for order #8823 and the tracking hasn't updated in
6 days. I need this sorted before my card statement closes.
```

### Prediction (before running)

- category: billing (could also argue delivery — message mixes a double
  charge with a stalled tracking update)
- sentiment: negative
- priority: high (money + time pressure from the statement closing)
- needs_order_lookup: yes (need to check the tracking/charge against the order)
- needs_faq_lookup: maybe (duplicate-charge dispute process)
- needs_human_review: yes (a duplicate charge is a financial issue, not
  something to resolve on the customer's say-so alone)

### Actual result

```json
{
  "analysis": {
    "summary": "Customer reports being charged twice for order #8823 and says tracking hasn't updated in 6 days; wants resolution before their card statement closes.",
    "category": "billing",
    "sentiment": "negative",
    "priority": "high",
    "needs_order_lookup": true,
    "needs_faq_lookup": true,
    "needs_human_review": true,
    "faq_query": "duplicate charge dispute and refund policy",
    "human_review_reason": "Resolving a duplicate charge requires financial verification and authorization beyond automated support."
  },
  "usage": {
    "model": "claude-sonnet-5",
    "input_tokens": 1567,
    "output_tokens": 307
  }
}
```

### Comparison

1. **Matched:** category (billing), sentiment (negative), priority (high),
   needs_order_lookup (yes), needs_human_review (yes).
2. **Differed:** I hedged on needs_faq_lookup ("maybe") — the model committed
   to `true` and, importantly, backed it with a concrete `faq_query`
   ("duplicate charge dispute and refund policy") instead of just flipping
   a boolean. That's more decisive than my prediction.
3. **Same schema:** yes — every group hitting `/analyse` gets the same
   `TicketAnalysis` shape back regardless of message content. The *fields*
   never change; only the *values* do. That's the whole point of a
   contract-first design.
4. **Constrained by the application:** field names, allowed enum values
   (category/sentiment/priority), the fact that booleans are booleans, and
   the conditional-required rule (`faq_query`/`human_review_reason` must be
   populated when their matching boolean is true) — none of this is up to
   the model, it's enforced by `TicketAnalysis`'s Pydantic validator.
5. **Remains AI judgement:** which enum value fits, whether each boolean
   is true or false, and the actual wording of `summary`, `faq_query`,
   `human_review_reason` — the schema says these fields must exist and
   obey the dependency rule, but not what they contain.

### Step 4 — invalid object

```python
invalid = {
    "summary": "Customer wants a callback about a billing issue.",
    "category": "billing",
    "sentiment": "negative",
    "priority": "high",
    "needs_order_lookup": False,
    "needs_faq_lookup": True,
    "needs_human_review": False,
    "faq_query": None,
    "human_review_reason": None,
}
```

This is syntactically valid data (every key exists, every value is the
right type) but breaks the app's contract: `needs_faq_lookup` is `True`
while `faq_query` is `None`.

### Validation result

```text
1 validation error for TicketAnalysis
  Value error, faq_query is required when needs_faq_lookup is true [type=value_error]
```

Rejected by `TicketAnalysis.validate_dependencies` (the `@model_validator`
in `app/schemas/ai.py`) — confirms the conditional-required rule is
actually enforced in code, not just documented as an intention.
