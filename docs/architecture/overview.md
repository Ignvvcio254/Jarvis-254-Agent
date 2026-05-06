# 📐 Architecture Overview

The Jarvis Framework is designed as a **Modular AI Engineering Operating System**. Instead of relying on a single large prompt, it distributes intelligence across multiple specialized layers.

## 🏗️ The Layered Architecture

### 1. The Routing Layer (The Pre-Processor)
At the very entrance of every prompt, the **Model Router** acts as a traffic controller. It analyzes the intent of the user and injects a "routing hint" into the context. This ensures that simple chat doesn't waste expensive Opus tokens, and complex architecture isn't handled by a fast-but-shallow model.

### 2. The Memory Layer (The Long-Term Storage)
Jarvis solves the "context window" problem using **Cerebro**. Unlike standard chat history, Cerebro is a **Structured Knowledge Vault**. It uses:
- **Session Nodes**: Raw captures of work.
- **Concept Nodes**: Synthesized abstractions.
- **ADRs**: Formalized technical decisions.
This creates a "Second Brain" that the agent can query to remember decisions made weeks ago.

### 3. The Behavioral Layer (The Protocol)
Jarvis doesn't just "act"; it follows **Protocols**. These are markdown-based specifications (located in `/core/behavior`) that define exactly how the agent should handle specific types of work (e.g., the Design Intelligence Protocol).

### 4. The Library Layer (The Toolset)
The **Skill Library** provides a standardized way to inject domain expertise. Each skill is a self-contained module with:
- Trigger patterns.
- Technical references.
- Implementation playbooks.

### 5. The Visual Layer (The Design System)
Jarvis treats UI as a science. By using **Visual Blueprints**, the agent can generate consistent, high-fidelity styles across different projects without "guessing" the look and feel.

## 🔄 Data Flow: A Request's Journey

`User Prompt` $\rightarrow$ `Model Router` $\rightarrow$ `Context Injection` $\rightarrow$ `Memory Retrieval (Cerebro)` $\rightarrow$ `Skill Activation` $\rightarrow$ `Execution` $\rightarrow$ `Memory Ingestion` $\rightarrow$ `Output`
