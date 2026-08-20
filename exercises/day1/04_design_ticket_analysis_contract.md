# Exercise 04 — Design an AI Output Contract

## Goal

Design the data contract your backend should receive from Claude before seeing the course implementation.

## Time

Approximately 15 minutes.

## Scenario

SupportOps AI receives customer-support messages.

Later application logic must be able to decide things such as:

- what type of support issue this is
- how the customer feels
- how important the issue is
- whether another system needs to be consulted
- whether a human should review the case

## Task

Design the JSON object you would want Claude to return.

Your design should be specific enough that normal Python code could validate it and make decisions from it.

Think about:

- field names
- allowed values
- booleans vs free text
- optional fields
- relationships between fields

## Deliverable

One proposed JSON example and a short explanation of the rules you would validate.

Do not implement the Pydantic model yet unless the instructor asks you to.

## Answers

### Proposed JSON

```json
{
  "summary": "Customer reports a repeated late-delivery issue and paid for expedited shipping.",
  "category": "delivery",
  "sentiment": "negative",
  "priority": "high",
  "needs_order_lookup": true,
  "needs_faq_lookup": false,
  "needs_human_review": false,
  "faq_query": null,
  "human_review_reason": null
}
```

### How I picked the fields

Went through the 5 things the scenario says the app needs to decide, and for each one asked: is this a fixed list of options, or a yes/no, or does it actually need free text?

- **What type of issue** → `category`. Made this a closed list instead of free text (delivery, return, refund, billing, product, account, general, other) because if Claude can write anything it wants here, my code can't switch/if on it reliably.
- **How the customer feels** → `sentiment`. Just positive / neutral / negative, keep it simple.
- **How important** → `priority`. low / medium / high / urgent — treated as ordered levels, not just labels, since priority is basically a queue-sorting decision.
- **Whether another system needs to be consulted** → I split this into two separate booleans instead of one: `needs_order_lookup` and `needs_faq_lookup`. Figured "another system" could mean two pretty different things (pull an order record vs check a policy/FAQ), and those trigger different code paths, so one flag wasn't enough.
- **Whether a human should review** → `needs_human_review`, plain boolean.
- Threw in a `summary` field too even though it's not one of the 5 listed — someone still has to read a one-line description of the ticket somewhere (dashboard, log, whatever), and none of the other fields give you that.

### Validation rules I'd want

- category / sentiment / priority can only be one of the allowed values, not any string.
- the needs_* fields have to be actual booleans.
- if `needs_faq_lookup` is true, `faq_query` can't be empty — otherwise what am I even looking up. Same idea for `needs_human_review` and `human_review_reason`.
- summary shouldn't be empty and probably needs a max length so nobody returns a wall of text.
- reject any extra fields Claude tries to sneak in that aren't part of the schema.

### Comparing to what's already in the repo

Turns out the instructor's own version of this was already sitting in the repo by the time I got to this exercise (came in with the same pull as the exercise file itself), so I checked my answer against `app/schemas/ai.py` after writing it, not before.

Pretty much lines up — same category/sentiment/priority values, same 3 needs_* booleans, same idea of faq_query/human_review_reason being conditionally required. Main thing theirs does that mine only described in words: they actually wire that "required if the boolean is true" rule into a Pydantic validator (`@model_validator`), so it's enforced automatically instead of just being something I said I'd check. They also forbid extra fields on every schema through one shared base class instead of repeating that rule everywhere.

### Tested the live /analyse endpoint — found a real issue

Ran a real support message through `POST /analyse` (the actual course implementation). Response was valid and the conditional-required rule worked exactly as designed (faq_query and human_review_reason both came back populated because their matching booleans were true).

But: `output_tokens` came back as exactly `500` — which is the `max_tokens` value hardcoded in `app/services/analysis_service.py`. That's not a coincidence, that's the ceiling. This particular response happened to finish cleanly with valid JSON, but `TicketAnalysis` has three free-text fields that can all need populating at once (summary + faq_query + human_review_reason). A longer or messier ticket could hit the same 500-token ceiling mid-object and come back as truncated, invalid JSON — which would fail the whole request, not just return a slightly-short answer.

**Flag for instructor:** is 500 tokens enough headroom for `TicketAnalysis` in the worst case, or should `max_tokens` be raised / field lengths tightened so this can't truncate mid-schema?
