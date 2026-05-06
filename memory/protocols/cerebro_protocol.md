# Cerebro Memory Protocol — Operational Schema

The `cerebro` system is the long-term reasoning and memory engine of the Jarvis Framework. It is a structured, interconnected Markdown wiki designed to prevent context loss across sessions and facilitate deep architectural recall.

---

## 📁 Directory Architecture

- `index.md` — The Dense Node Catalog. The primary entry point for all queries and ingestion.
- `log.md` — Append-only operation log. Tracks wiki-level changes (ingest, lint, merge).
- `sources.md` — External source registry. A directory of truth, not a content cache.
- `sessions/` — Session nodes. Individual files capturing specific units of work.
- `concepts/` — Emergent knowledge nodes. High-level abstractions derived from sessions.
- `adr/` — Architecture Decision Records. Formal logs of technical trade-offs.

---

## 🧬 Node Life Cycle

1. **Birth**: Every new entry starts as a `session` node.
2. **Observation**: The system tracks recurring patterns across nodes.
3. **Emergence**: When a term or concept appears in 3+ nodes, it is flagged during `lint` as a candidate for a `concept` node.
4. **Solidification**: Concept nodes are created to synthesize cross-session knowledge.
5. **Supersession**: When a decision is changed, the old node is marked `status: superseded` and linked to the new one via `superseded_by`.

---

## 🛠️ Core Operations

### 1. Ingestion (`/memory ingest`)
When capturing a session:
1. **Analyze**: Identify Area, Action Verb, Output, Decisions, and Pendings.
2. **Slug Generation**: `YYYY-MM-DD-<kebab-case>`. Focus on the *result*, not the process.
3. **Deduplication**: If a similar node exists for the same day, append to it as an `Update [HH:MM]`.
4. **Cross-Linking**: Identify related nodes via tags and proximity.
5. **Bidirectional Sync**: Every link in `related` must have a reciprocal link in the target node's `Cross-refs`.
6. **Indexing**: Update `index.md` and `log.md`.

### 2. Querying (`/memory query`)
When retrieving information:
1. **Scan**: Read `index.md` to identify 1-5 candidate nodes.
2. **Analyze**: Read candidate nodes fully.
3. **Verify**: If the query depends on a file, read the file directly from the repository (the wiki stores pointers, not copies).
4. **Synthesize**: Provide a response with citations using wikilinks `[[slug]]`.

### 3. Linting (`/memory lint`)
Periodic maintenance to ensure integrity:
- **Orphan Detection**: Find nodes with no inbound links.
- **Link Validation**: Detect broken `[[slug]]` references.
- **Pattern Recognition**: Identify emerging concepts.
- **Consistency Check**: Find contradictions without `superseded_by` markers.
- **Index Sync**: Ensure the folder state matches `index.md`.

---

## 🔗 Link Convention: Wikilinks

**CRITICAL RULE**: All internal wiki links must use the `[[slug]]` format (compatible with Foam/Obsidian).

- **Syntax**: `[[slug]]` (filename without `.md`, no path).
- **Usage**: 
  - `index.md` entries.
  - `## Cross-refs` sections.
  - `## Sources` internal anchors.
- **External References**: Use standard Markdown `[text](url)` for URLs and backticks for files outside the `cerebro/` vault.
