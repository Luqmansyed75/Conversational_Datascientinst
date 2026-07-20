# AGENT.md

# Conversational Data Scientist using Multi-Agent Orchestration

## Project Overview

Build an AI-powered Conversational Data Scientist capable of answering natural language questions by combining Retrieval-Augmented Generation (RAG), SQL querying, Machine Learning analysis, and Multi-Agent Orchestration.

Instead of relying on a single LLM, the system coordinates multiple specialized AI agents using LangGraph. Each agent performs a dedicated task while sharing context through a common state.

The objective is to allow non-technical users to obtain insights from documents and structured data simply by chatting with the system.

---

# Problem Statement

Organizations store information in multiple formats:

* PDF documents
* Company manuals
* Sales reports
* Databases
* CSV files
* Internal documentation

Finding information usually requires searching multiple sources or writing SQL queries manually.

Business users without technical knowledge struggle to retrieve insights quickly.

---

# Proposed Solution

Develop a Multi-Agent AI system that accepts natural language questions and intelligently decides:

* Retrieve information from documents (RAG)
* Query structured databases
* Perform data analysis
* Generate predictions
* Merge responses into one final answer

The orchestration is handled by LangGraph.

---

# Tech Stack

## AI Frameworks

* LangChain
* LangGraph

## LLM

* OpenAI / Gemini / Groq
* Ollama (optional local model)

## Vector Database

* ChromaDB
* FAISS

## Database

* SQLite (development)
* PostgreSQL (production)

## Embedding Model

* sentence-transformers
* BAAI/bge-small-en
* all-MiniLM-L6-v2

(Local embeddings preferred.)

## NLP

* SpaCy

## ML

* NumPy
* Pandas
* Scikit-learn

## MCP

* SQL MCP Server
* Filesystem MCP Server
* CSV MCP Server

## Frontend

* Streamlit

---

# Multi-Agent Architecture

## 1. Intent Router Agent

### Responsibility

Determine the user's intent.

Possible intents:

* Document Retrieval
* SQL Query
* Data Analysis
* Prediction
* Hybrid Query

Output:

```text
Intent + Required Agents
```

---

## 2. RAG Agent

### Responsibility

Retrieve relevant company documents.

Pipeline

User Question

↓

Vector Search

↓

Relevant Documents

↓

LLM

↓

Answer

Uses:

* ChromaDB
* Embedding Model
* LangChain Retriever

---

## 3. SQL Agent

### Responsibility

Convert natural language into SQL.

Example

User:

"What were Laptop sales last month?"

↓

Generate SQL

↓

Execute SQL

↓

Return Results

Uses:

* SQLite/PostgreSQL
* MCP SQL Server

---

## 4. ML Analysis Agent

### Responsibility

Perform analytics.

Examples

* Forecast sales
* Detect trends
* Calculate growth
* Identify anomalies

Uses

* NumPy
* Pandas
* Scikit-learn

---

## 5. Response Synthesizer Agent

### Responsibility

Merge outputs from every agent.

Example

Input

RAG Output

*

SQL Output

*

ML Output

↓

Generate one coherent response.

---

# LangGraph Workflow

```text
                  User Query
                       │
                       ▼
              Intent Router Agent
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
  RAG Agent       SQL Agent      ML Analysis Agent
      │                │                │
      └────────────────┼────────────────┘
                       ▼
          Response Synthesizer Agent
                       │
                       ▼
                 Final Response
```

---

# Shared State

The graph maintains:

* Conversation history
* Retrieved documents
* SQL results
* ML outputs
* Current intent
* Entity information
* User preferences
* Time filters

---

# Folder Structure

```text
project/

│

├── agents/

│   ├── router_agent.py

│   ├── rag_agent.py

│   ├── sql_agent.py

│   ├── ml_agent.py

│   └── synthesizer_agent.py

│

├── graph/

│   ├── graph.py

│   ├── state.py

│   └── nodes.py

│

├── mcp/

│   ├── sql_server.py

│   ├── filesystem_server.py

│   └── csv_server.py

│

├── rag/

│   ├── ingest.py

│   ├── embeddings.py

│   └── retriever.py

│

├── database/

│

├── datasets/

│

├── models/

│

├── ui/

│   └── app.py

│

└── main.py
```

---

# Development Principles

* Every agent should perform only one responsibility.
* Agents communicate only through LangGraph State.
* Avoid business logic inside the graph.
* Keep prompts modular.
* Use MCP for external tools.
* Prefer local models whenever possible.
* Minimize external API dependencies.

---

# Initial Version (V1)

The first version should support:

* Chat interface
* PDF document retrieval
* SQLite querying
* RAG
* SQL Agent
* Response synthesis
* Conversation memory

ML forecasting can be added in Version 2.

---

# Future Enhancements

* Multi-database support
* Chart generation
* Voice interface
* Dashboard generation
* CSV upload
* Excel support
* Web search agent
* Email report generation
* Autonomous planning agent
* Human-in-the-loop approval

---

# Success Criteria

The system should be able to:

* Answer questions from company documents.
* Retrieve structured data from SQL databases.
* Combine multiple data sources.
* Maintain conversational context.
* Produce accurate, explainable answers.
* Demonstrate effective Multi-Agent Orchestration using LangGraph.

---

# Primary Goal

Create a production-style AI system that showcases:

* Multi-Agent Systems
* LangGraph Orchestration
* RAG Pipelines
* MCP Integration
* LLM Tool Calling
* SQL Agents
* Machine Learning Integration
* Conversational AI
