# Exercise 01 — Secure Order Lookup

## Goal

Implement an order lookup that returns an order only when it belongs to the
current customer.

## Time

Approximately 20 minutes.

## Starting point

The application is connected to MongoDB.

You have:

```text
app/schemas/order.py
app/repositories/order_repository.py
```

The repository method is incomplete.

## Business requirement

SupportOps must retrieve order details for a support request.

Knowing an `order_id` alone must not allow a caller to retrieve another
customer's order.

## Task

Implement:

```text
OrderRepository.get_order_for_customer(...)
```

Use the existing method arguments, projection, and `OrderContext` model.

**Before coding**, write down the MongoDB query your pair believes is correct.

Your implementation should:

- query by both `customer_id` and `order_id`;
- use the existing projection;
- return an `OrderContext` when an authorized record exists;
- return `None` when no authorized record exists.

## Expected behaviour

The same `order_id` must not be retrievable under a different customer ID.

## Questions

1. Why is the customer identifier part of the lookup?
2. Why does the repository use a projection?
3. Should Claude decide whether a customer may access a different order?
4. What should the repository return when no authorized order is found?

## Deliverable

Show the query your pair chose and explain why it enforces the business
requirement.

## Answers

### Query written before checking the repository

```python
database.orders.find_one(
    {"customer_id": customer_id, "order_id": order_id},
    ORDER_CONTEXT_PROJECTION,
)
```

Filter on both fields together, not `order_id` alone — a document only
matches if it belongs to that exact customer *and* has that exact
`order_id`. Apply `ORDER_CONTEXT_PROJECTION` so only an allow-listed set
of fields ever leaves the database layer.

### Comparing to the instructor's solution

Already implemented in `app/repositories/order_repository.py`
(`get_order_for_customer`) by the time I got to this exercise — matches
exactly: same two-field filter, same projection, `None` on no match,
`OrderContext.model_validate(document)` on a match.

### Questions

1. **Why is the customer identifier part of the lookup?** Because
   `order_id` alone isn't a secret — it's often visible in emails,
   receipts, or guessable sequential IDs. Scoping every query to
   `customer_id` too means a caller can never pull someone else's order
   just by knowing (or guessing) an ID that isn't theirs.
2. **Why does the repository use a projection?** So the database layer
   only ever returns an allow-listed set of fields (`order_id`, `status`,
   `items`, `estimated_delivery`, `delivered_at`) — not the raw document.
   Anything not on that list (internal flags, other customers' notes,
   payment details, whatever else lives on the order document) never
   leaves the repository, regardless of what gets added to the schema
   later.
3. **Should Claude decide whether a customer may access a different
   order?** No. Authorization is a `customer_id`/`order_id` match done in
   MongoDB before Claude ever sees anything. Claude only receives
   whatever `OrderContext` the repository already decided was
   authorized — it has no path to request or reason about a different
   order.
4. **What should the repository return when no authorized order is
   found?** `None` — not an error, not an empty-but-truthy object. `None`
   is deliberately indistinguishable between "order doesn't exist" and
   "order exists but belongs to someone else" — the caller shouldn't be
   able to tell the difference either, since confirming an order ID
   exists under another account is its own information leak.

### Live test

```text
POST /generate-response
{"customer_message": "...", "customer_id": "CUST-101", "order_id": "ORD-1001"}
```
→ 200, order returned, used in the drafted response.

```text
POST /generate-response
{"customer_message": "...", "customer_id": "CUST-102", "order_id": "ORD-1001"}
```
→ 200, but `get_order_for_customer` returns `None` (ORD-1001 belongs to
CUST-101, not CUST-102) — confirmed the same `order_id` is not
retrievable under a different customer. See Exercise 02 for the full
grounded-response test log.
