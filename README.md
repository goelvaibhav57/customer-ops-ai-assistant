# Customer & Ops Intelligence Agent – Capstone Project

## 📌 Overview

This project implements an end-to-end **Customer & Operations Intelligence Agent** designed for automated support workflows. It is built using a combination of **RAG**, **FASTAPI**, **MCP tools**, **intent classification**, and a **graph-based agent architecture**. The solution can answer FAQs, perform structured data lookups, escalate unclear queries, synthesize final responses, and leverage conversational history for follow-ups.

---

## 🚀 Key Features

### 1. **Retrieval-Augmented Generation (RAG) for FAQ Node**

* Built a RAG pipeline to retrieve relevant information from a knowledge base.
* Used for handling FAQ-type queries.
* Ensures accurate and contextually relevant responses.
* Not used Splitting and chunking as not required for current dataset.

### 2. **Custom Tools for CSV Data Lookup**

* Built MCP (Model Context Protocol) tools to fetch structured data from CSV files.
* Supports data queries for:

  * Account details
  * Invoices
  * Tickets
  * Usage
* These tools integrate seamlessly with the agent.

### 3. **MCP Server Integration**

* Created a dedicated MCP server to manage tool execution.
* Provides reliable communication between tools and the agent.

### 4. **FASTAPI Endpoints for Tool & Agent Access**

* Exposed the tools and agent logic using FASTAPI.
* The agent executor can be triggered via API endpoints.
* Clean separation of concerns between interface, logic, and tooling.

### 5. **Graph-Based Agent Workflow**

* Implemented a graph where each node represents a functional component:

  * **Intent Classifier Node** → Determines whether the query is FAQ, DataLookup, or Escalate.
  * **FAQ Node (RAG)** → Answers general informational queries.
  * **DataLookup Node** → Fetches structured data using CSV tools.
  * **Escalate Node** → Handles unclear or unsupported queries.
  * **Synthesize Node** → Produces final user-friendly answers with citations.
* The graph routes the query flow based on node outputs.

### 6. **Synthesize Node for Final Responses**

* Combines tool outputs, knowledge base responses, and conversation history.
* Formats responses in user-friendly language.
* Includes source citations using Pydantic models.

### 7. **Conversation History Tracking**

* Stores the full history of user interactions.
* Enables contextual follow-up answers.
* History is also used by the Synthesize node to refine responses.


---

## 🎨 Streamlit UI

* Added a Streamlit-based web UI to interact with the agent directly from the browser.
* Provides an easy interface to test FAQ, data lookups, and escalation workflows.
* Supports streaming responses and displays conversation history.

### ▶️ Run Streamlit UI

```
cd src
streamlit run app.py
```

## 🏗️ System Architecture

```
User Query
   ↓
Intent Classifier
   ↓
 ┌───────────────┬────────────────┬
 │ FAQ (RAG)     │ Data Lookup    │
 └───────────────┴────────────────┴
   ↓
 ┌───────────────┬────────────────┬
 │ Synthesize    │ Escalate Node  │
 └───────────────┴────────────────┴  
   ↓
Final Response (with citations)
```

---

## 🛠️ Tech Stack

* **Python**
* **FastAPI** for API layer
* **LangChain / LangGraph** for agent graph and orchestration
* **MCP Tools** for CSV data interaction
* **RAG** using embeddings and vector search
* **Pydantic** for structured response models

---

## ▶️ How to Run

### 1. Install dependencies:

```
pip install -r requirements.txt
```

### 2. Start MCP server:

```
python tools/server.py
```

### 4. Run main app:

* streamlit run src/app.py

---

## 📚 Future Improvements

* Add analytics dashboard for queries.
* Expand the agent with more nodes.
* Add authentication for sensitive operations.
* Improve vector search relevance using better embeddings.

---

## 📝 Notes

This project demonstrates a complete intelligent agent pipeline suitable for enterprise customer support and operational intelligence workflows.

---

## 💬 Contact

For questions or improvements, feel free to reach out!
