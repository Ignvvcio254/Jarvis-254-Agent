# Node Schema Definition

All nodes in the Cerebro system must adhere to the following structure to ensure programmatic indexability and agent-led reasoning.

## 📋 Frontmatter (YAML)

Every node must start with this exact YAML block:

```yaml
---
type: session # session | concept | adr | person | entity
area: <dev | design | ai | ops | personal | jarvis>
date: YYYY-MM-DD
slug: <kebab-case-slug>
title: "<Human Readable Title>"
tags: [tag1, tag2]
status: active # active | superseded | archived
related:
  - <slug-of-related-node>
sources:
  - repo:<relative/path/to/file>
  - url:<full-url>
superseded_by: null # slug of the replacing node
---
```

### Field Constraints
- **slug**: The unique identifier. Must match the filename without `.md`. Max 6 words.
- **area**: Must be one of the predefined areas. If a session spans multiple, create cross-links.
- **related**: Maximum 5 related slugs.
- **sources**: Use `repo:` or `url:` prefixes.

---

## 📝 Body Structure

Nodes must follow this sequential section order:

### `# <Node Title>`
The main heading must be the human-readable title.

### `## Context`
The "Why" and "What". What triggered this session? What was the starting state?

### `## Decisions`
The "How". Log every technical decision and its rationale. Use a bulleted list.

### `## Output`
The "Result". List files created, modified, or external links produced.

### `## Pending`
The "Next". Explicit tasks or unanswered questions left for future sessions.

### `## Cross-refs`
Bidirectional links to other nodes:
- `[[slug]]` — Concise reason for the connection.

### `## Sources`
Direct pointers to truth:
- `[[sources#id]]` — Pointer to the central source index.
- `repo:path/to/file` — Direct repository reference.
- `[Label](URL)` — External web reference.
