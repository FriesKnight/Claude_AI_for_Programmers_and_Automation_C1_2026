# End-of-Day AI Build Challenge

## Objective

Working in a small group, build a **small working backend application that uses the Claude API** and demonstrates the main engineering ideas covered during the course.

The goal is **not** to build a large or polished product.

Your goal is to show that your group can take the ideas we have worked through during the course and apply them to a new problem.

> **A small working application that you understand is better than a large unfinished application.**

You will have approximately **90 minutes to build**, followed by a short group presentation.

---

## Groups

You will work in **3 groups**, with approximately **2–3 participants per group**.

Everyone in the group should understand the overall application, even if different people focus on different parts.

Possible responsibilities include:

- API / Claude integration
- Database / workflow
- Validation / testing / prompts

These are not strict roles. You are encouraged to work together.

---

## Technology

### Programming language

You may use **any backend programming language or framework** that your group is comfortable with.

For example:

- Python + FastAPI
- PHP + Laravel
- Java + Spring Boot
- JavaScript / TypeScript + Express
- Another backend framework your group is comfortable with

The course examples have used Python and FastAPI, but this project is about applying the **architecture and AI engineering principles**, not testing your Python syntax.

---

## AI coding tools are allowed

You may use:

- Claude Code
- ChatGPT
- GitHub Copilot
- IDE AI assistants
- Another AI coding assistant

You may use these tools to help with:

- Project scaffolding
- Framework syntax
- Claude SDK integration
- Debugging
- Boilerplate
- Validation models
- Refactoring
- Testing

There is one important condition:

> **You are responsible for understanding the code that your group submits.**

During the presentation, any member of the group may be asked to explain how part of the application works.

---

## Your application must use Claude

Using an AI assistant **to write your code** does not count as the Claude integration.

Your application itself must make at least one real integration with the **Claude API**.

For example:

```text
Developer
   ↓
uses Claude Code to help write Laravel

Laravel application
   ↓
calls Claude API

✓ valid
```

This would not satisfy the requirement:

```text
Developer
   ↓
uses an AI assistant to generate project

Application
   ↓
never calls Claude

✗ not sufficient
```

---

## What should you build?

Choose a small problem that can be demonstrated through an API.

Possible ideas include:

### AI Report Generator

Analyse supplied information and generate a structured report.

### AI Customer Support API

Analyse customer messages, retrieve information and generate responses.

### AI Document Analyzer

Submit text or a document and extract structured information or classifications.

### AI Workflow Automation Tool

Analyse a request and execute a controlled multi-step workflow.

### Your own idea

You may propose another idea as long as it demonstrates the required course concepts.

---

## Your group should aim to demonstrate all of the following.

### 1. A backend REST API

Your application exposes API endpoints that can be tested using Postman, curl, Swagger/OpenAPI, or another API client.

A frontend is **not required**.

### 2. Claude API integration

Your backend makes real calls to Claude.

The Claude API key must not be hard-coded into source code.

For example:

```text
.env

ANTHROPIC_API_KEY=...
```

### 3. At least two AI-powered endpoints

For example:

```text
POST /analyse
POST /generate
```

or:

```text
POST /classify-document
POST /generate-report
```

The two endpoints do not need to be extremely complicated.

### 4. At least one structured Claude response

At least one operation should ask Claude to return information in a predictable structure.

For example:

```json
{
  "category": "billing",
  "priority": "high",
  "summary": "Customer disputes an invoice",
  "requires_review": true
}
```

Your application should validate that structure before trusting it.

### 5. MongoDB

Your application should use MongoDB to **store or retrieve useful application data**.

Examples:

- Save analysis results
- Retrieve customer information
- Store generated reports
- Retrieve approved reference information
- Save workflow results

### 6. A multi-step workflow

At least one operation should involve more than:

```text
request
→ Claude
→ response
```

For example:

```text
validate request
    ↓
ask Claude to analyse
    ↓
retrieve data from MongoDB
    ↓
generate response
    ↓
store result
    ↓
return API response
```

### 7. Input and output validation

Your application should validate incoming API requests.

You should also avoid blindly trusting AI-generated output.

Think about:

- Required fields
- Types
- Length limits
- Allowed values
- Structured AI output
- Missing data

### 8. Basic failure handling

Your application should handle at least one realistic failure safely.

For example:

- Bad user input
- Claude API failure
- Invalid Claude output
- Database record not found
- MongoDB failure

The application should return a controlled response rather than simply crashing.

### 9. Basic security

At minimum:

- API keys are stored outside source code
- User input is treated as untrusted
- AI output is not automatically trusted
- The application controls database access and actions

> **Claude can assist with decisions and generation, but the application SHOULD control data access, validation, permissions and business actions.**

---

## Keep the project small

You have approximately **90 minutes**.

You do **not** need to build:

- A frontend
- Authentication UI
- Docker or Kubernetes
- Microservices
- Deployment infrastructure
- Vector databases
- A large agent system
- A production-ready architecture

Do not spend half of the project creating infrastructure that you cannot demonstrate.

Focus on the AI/backend workflow.

---

## Optional extensions

Only attempt these if your required functionality already works.

Possible extensions include:

- Claude tool calling
- Agentic decision-making
- Request logging
- Token usage tracking
- Cost estimation
- Caching
- Additional external APIs
- Additional security controls
- More advanced workflows

---

## Before you start coding

Your group should be able to answer these questions:

```text
Problem:
What problem are we solving?

AI endpoint 1:
What does Claude do?

AI endpoint 2:
What does Claude do?

MongoDB:
What information do we store or retrieve?

Workflow:
What happens from request to final response?
```

Be prepared to show these answers to the instructor before you begin building.

---

## Presentation

Each group has a maximum of **10 minutes**.

You do not need to use the full 10 minutes.

Suggested structure:

- **1 minute** — What did you build and why?
- **3 minutes** — Demonstrate the API working.
- **2 minutes** — Explain the architecture and workflow.
- **1–2 minutes** — Explain one validation, security or reliability decision.
- **Remaining time** — Questions.

Do not walk through every source-code file. We are interested in the **engineering decisions and working system**.

---

## Final reminder

> **Build something small, make it work, understand it, and be ready to explain it.**
