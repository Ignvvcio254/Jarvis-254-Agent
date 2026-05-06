# 🧠 The Memory Engine (Cerebro)

Cerebro is the long-term memory architecture of the Jarvis Framework. It transforms the ephemeral nature of AI sessions into a persistent, searchable, and evolving knowledge graph.

## ⚙️ How it Works

Cerebro is implemented as a **Local Markdown Wiki** using wikilinks (`[[slug]]`), making it compatible with tools like Foam and Obsidian.

### The Node Hierarchy
1. **Session Nodes**: The raw data. Every session is logged.
2. **Concept Nodes**: The synthesized data. When a pattern appears in 3+ sessions, it becomes a concept.
3. **ADRs (Architecture Decision Records)**: The "Why". A formal record of a technical choice.

### The Operational Cycle
- **Ingest**: The agent captures the essence of a session $\rightarrow$ creates a node $\rightarrow$ links it to related nodes.
- **Query**: The agent scans the index $\rightarrow$ identifies relevant nodes $\rightarrow$ synthesizes a response based on historical truth.
- **Lint**: A periodic maintenance process that finds broken links, orphan nodes, and emerging concepts.

## 🛠️ Implementation for Developers

To initialize Cerebro in a new project:
1. Run the installer.
2. The system creates the `.claude/cerebro/` directory.
3. The agent follows the `cerebro_protocol.md` to manage the wiki.

### Example Node Structure
All nodes must include:
- **Frontmatter**: Metadata for programmatic indexing.
- **Context**: The starting point.
- **Decisions**: The rationale.
- **Output**: The result.
- **Cross-refs**: The connections.
