---
title: ResolveAI
emoji: 🛠️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.38.0"
app_file: app.py
pinned: false
---

# ResolveAI 🛠️

**An AI-powered order dispute resolution system for Stryde (a fictional retail/sportswear brand)**

ResolveAI automates the investigation, policy reasoning, and customer response process for order disputes — refunds, damaged items, warranty claims — using a multi-agent system built with LangGraph and the Model Context Protocol (MCP).

🔗 **Live Demo:** [link here once deployed]
📂 **GitHub:** [link here]

---

## What It Does

A customer describes an issue with their order (e.g., "my shoes arrived damaged" or "the sole separated after 5 months"). ResolveAI:

1. **Investigates** — looks up the order, customer, and product details
2. **Reasons** — retrieves the relevant policy (returns/warranty) and decides: **Approved**, **Denied**, or **Escalate**
3. **Responds** — drafts a clear, empathetic customer-facing message, or routes to human review if the case is genuinely ambiguous

---

## Architecture
Customer Message

↓

[Investigator Agent] → looks up order/customer/product facts (MCP tools)

↓

[Policy Reasoner Agent] → RAG search over policy docs, makes a decision (MCP tools)

↓

┌──────────────┴──────────────┐

APPROVED/DENIED              ESCALATE

↓                            ↓

[Response Drafter]      [Human Handoff — fixed message]

↓                            ↓

Final Response

Orchestrated with **LangGraph**, using conditional edges to route ambiguous cases away from automated response generation.

---

## Tech Stack

- **Orchestration:** LangGraph (multi-agent state graph, conditional routing)
- **Tool Layer:** Model Context Protocol (MCP) — order lookup, customer lookup, policy search exposed as standardized tools
- **Retrieval:** ChromaDB + OpenAI `text-embedding-3-small`, with custom table-aware chunking to preserve markdown tables (warranty coverage tables) as atomic units
- **LLM:** GPT-4o
- **UI:** Streamlit
- **Data:** Synthetic Stryde retail dataset (orders, products, customers) + policy docs (returns, warranty, shipping)

---

## Key Design Decisions

- **Three agents, not one** — Investigator, Policy Reasoner, and Response Drafter are separated because each step has a genuine sequential dependency: policy reasoning needs facts gathered first, and response drafting needs a decision made first. This isn't simple routing — it's a chain of dependent reasoning steps.
- **Table-safe chunking** — standard recursive text splitting broke markdown tables mid-row, corrupting warranty coverage lookups. Built a custom preprocessing step that detects and preserves tables as atomic chunks before applying standard chunking to surrounding prose.
- **Escalation over guessing** — initial testing showed the Policy Reasoner would confidently approve/deny claims based on partial keyword similarity to policy text, even when the actual situation wasn't clearly addressed. Added an explicit instruction to escalate to human review when the retrieved policy doesn't *fully and explicitly* cover the claim, rather than risk an incorrect automated decision.
- **Deterministic escalation message** — the human handoff path uses a fixed template rather than an LLM-generated message, since an ambiguous case shouldn't be paired with an LLM improvising commitments to the customer.

---

## Setup

```bash
# clone the repo
git clone <repo-url>
cd ResolveAI

# create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux

# install dependencies
pip install -r requirements.txt

# add your OpenAI API key
echo OPENAI_API_KEY=your_key_here > .env

# build the vector store (one-time setup)
python tools/vectorstore.py

# run the app
streamlit run app.py
```

---

## Project Structure
ResolveAI/

├── agents/              # Investigator, Policy Reasoner, Response Drafter

├── tools/               # MCP-wrapped lookup and retrieval functions

├── data/                # Synthetic Stryde dataset (JSON + policy markdown)

├── vectorstore/         # ChromaDB persistence (generated, not committed)

├── mcp_server.py        # MCP server exposing tools to agents

├── graph.py             # LangGraph orchestration

├── app.py               # Streamlit UI

└── setup_data.py        # Data loading utilities