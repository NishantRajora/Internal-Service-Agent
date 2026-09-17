# 🤖 Veridian Corp AI IT Support Agent

An intelligent, agentic IT support system designed for Veridian Corp. This project demonstrates a professional, full-stack AI agent capable of understanding employee issues, retrieving relevant company policies, making reasoned decisions based on historical precedents, and managing an integrated IT ticketing system.

## 🚀 Project Overview

The system acts as an automated first-line IT support engineer. Unlike a standard chatbot, it employs an **Agentic Workflow** to ensure that every response is grounded in company policy and consistent with previous decisions.

### 🔄 Agentic Workflow
**Employee Request** $\rightarrow$ **Intent Classification** $\rightarrow$ **Hybrid Policy Retrieval** $\rightarrow$ **Reasoning (with History)** $\rightarrow$ **Decision** $\rightarrow$ **Resolution / Escalation**.

### ✨ Key Features
- **Natural Language Understanding:** Automatically classifies user requests into specific IT categories using LLM-based intent detection.
- **Grounded Reasoning (RAG):** Implements a Retrieval-Augmented Generation (RAG) pattern using a curated Knowledge Base (KB) to prevent AI hallucinations.
- **Context-Aware Decisions:** Analyzes historical ticket data to maintain consistency in approvals, rejections, and resolution paths.
- **Secure Admin Dashboard:** A protected management area for IT admins to track tickets, review full audit trails, and manage policy grounding.
- **Automated Ticketing:** Intelligently decides when a request can be self-serviced vs. when it requires a structured IT ticket for human intervention.
- **Professional Full-Stack UI:** Modern web frontend built with HTML, CSS, and JavaScript, powered by a high-performance FastAPI backend.

---

## 📁 File Structure & Component Map

### ⚙️ Backend (Python/FastAPI)
| File | Description |
| :--- | :--- |
| `main.py` | **Entry Point.** FastAPI server handling routing, static file serving, and API endpoints for support and admin management. |
| `agent.py` | **The Brain.** Orchestrates the AI workflow. Handles LLM-based classification, decision-making, and response generation via the Ollama API. |
| `retriever.py` | **Knowledge Fetcher.** Implements a hybrid retrieval strategy (Category Mapping $\rightarrow$ Keyword Scoring) to fetch the most relevant policy from `policies.json`. |
| `database.py` | **Data Layer.** Manages the SQLite database (`veridian_it.db`) for tickets, audit logs, and system settings. |
| `auth_utils.py` | **Security.** Provides secure password hashing and verification using the `bcrypt` library. |
| `set_admin_password.py` | **Setup Utility.** Standalone script to securely initialize or update the admin dashboard password. |
| `seed_tickets.py` | **Data Utility.** Populates the database with historical ticket data from `tickets.json` to provide context for the AI. |

### 📚 Data & Configuration
| File | Description |
| :--- | :--- |
| `policies.json` | **Knowledge Base.** The "Ground Truth" containing official Veridian Corp IT policies (KB-01 to KB-10). |
| `tickets.json` | **Historical Data.** A dataset of past tickets used to seed the database and provide precedent for the AI's reasoning. |
| `requirements.txt` | **Dependencies.** Required Python libraries (FastAPI, Uvicorn, Requests, Bcrypt, Python-Dotenv). |
| `.env` | **Environment Variables.** Configuration for the Ollama API (Base URL, Model, and API Key). |

### 🎨 Frontend (Static Assets)
| File | Description |
| :--- | :--- |
| `static/index.html` | **UI Structure.** The main interface featuring the chat portal and the Admin Dashboard. |
| `static/style.css` | **Styling.** Modern corporate aesthetic with a responsive layout. |
| `static/script.js` | **Frontend Logic.** Handles API communication, session management, and dynamic DOM updates. |

---

## 🛠️ Installation & Setup

### 1. Clone and Install
```bash
# Install required dependencies
pip install -r requirements.txt
```

### 2. Configure AI Model
Create a `.env` file in the root directory. The system defaults to `llama3` via Ollama:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=your_api_key_here (optional)
OLLAMA_MODEL=llama3
```

### 3. Initialize System
Before starting the server, you must set the admin password and seed the database with historical context:
```bash
# Set the password for the Admin Dashboard
python set_admin_password.py

# Populate the database with historical precedents
python seed_tickets.py
```

### 4. Run the Server
```bash
python main.py
```
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to access the portal.

---

## 🛡️ Admin Access & API

### Admin Dashboard
To manage the system:
1. Navigate to the **Admin** tab in the web portal.
2. Enter the password created during the setup step.
3. Manage **Tickets**, review the **Audit Trail**, and browse the **Knowledge Base**.

### Key API Endpoints
| Endpoint | Method | Description | Access |
| :--- | :--- | :--- | :--- |
| `/api/support/request` | `POST` | Submit a support request to the AI Agent | Public |
| `/api/support/my-tickets`| `GET` | Get tickets for a specific employee email | Public |
| `/api/admin/login` | `POST` | Authenticate admin and receive session token | Public |
| `/api/support/tickets` | `GET` | List all system tickets | Admin |
| `/api/support/audit` | `GET` | Retrieve the full agent audit trail | Admin |
| `/api/support/policies` | `GET` | Retrieve the current knowledge base | Admin |
