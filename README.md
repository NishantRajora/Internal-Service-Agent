# 🤖 Veridian Corp AI IT Support Agent

An intelligent, agentic IT support system designed for Veridian Corp. This project demonstrates a full-stack AI agent capable of understanding employee issues, retrieving relevant company policies, making reasoned decisions based on historical precedents, and managing an IT ticketing system.

## 🚀 Project Overview

The system acts as an automated first-line IT support employee. Instead of a simple chatbot, it follows an agentic workflow:
**Employee Request** $\rightarrow$ **Intent Classification** $\rightarrow$ **Policy Retrieval** $\rightarrow$ **Reasoning (with History)** $\rightarrow$ **Decision** $\rightarrow$ **Resolution / Escalation**.

### Key Features
- **Natural Language Understanding:** Classifies user issues into specific IT categories.
- **Grounded Reasoning:** Uses a provided Knowledge Base (KB) to ensure responses are based on actual company policy.
- **Context-Aware Decisions:** analyzes historical tickets to maintain consistency in approvals and rejections.
- **Secure Admin Dashboard:** Protected area for IT admins to track tickets, review audit trails, and manage policies.
- **Automated Ticketing:** Creates structured IT tickets automatically when human intervention is required.
- **Full-Stack Interface:** Professional web frontend built with HTML, CSS, and JS, powered by a FastAPI backend.

---

## 📁 File Structure & Component Map

### ⚙️ Backend (Python/FastAPI)
| File | Description |
| :--- | :--- |
| `main.py` | **Entry Point.** The FastAPI server that handles routing, serves the frontend, and provides API endpoints for support requests and admin management. |
| `agent.py` | **The Brain.** Contains the AI logic for classification, decision-making, and response generation. Integrates with the Ollama API. |
| `retriever.py` | **Knowledge Fetcher.** Handles the logic for searching and retrieving the most relevant policy from the knowledge base. |
| `database.py` | **Data Layer.** Manages the SQLite database (`veridian_it.db`), including tables for tickets, audit logs, and system settings. |
| `auth_utils.py` | **Security.** Handles secure password hashing and verification using `bcrypt`. |
| `set_admin_password.py` | **Setup Utility.** A standalone script to securely initialize or change the admin password. |
| `seed_tickets.py` | **Data Utility.** Populates the database with historical ticket data from `tickets.json` for AI context. |

### 📚 Data & Configuration
| File | Description |
| :--- | :--- |
| `policies.json` | **Knowledge Base.** Contains all official Veridian Corp IT policies (KB-01 to KB-10). |
| `tickets.json` | **Historical Data.** A JSON list of past tickets used to seed the database and provide precedent for the AI. |
| `requirements.txt` | **Dependencies.** List of Python libraries required to run the project (FastAPI, Uvicorn, Requests, etc.). |
| `.env` | **Environment Variables.** Stores sensitive configuration like `OLLAMA_API_KEY` and `OLLAMA_MODEL`. |

### 🎨 Frontend (Static Assets)
| File | Description |
| :--- | :--- |
| `static/index.html` | **UI Structure.** The main page featuring the onboarding screen, chat interface, and admin dashboard. |
| `static/style.css` | **Styling.** Modern, professional corporate styling for the entire application. |
| `static/script.js` | **Frontend Logic.** Handles API interactions, user session state, and dynamic UI updates. |

---

## 🛠️ Installation & Setup

### 1. Clone and Install
```bash
pip install -r requirements.txt
```

### 2. Configure AI Model
Create a `.env` file in the root directory:
```env
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_API_KEY=your_api_key_here
OLLAMA_MODEL=gpt-oss:20b
```

### 3. Initialize System
Set the admin password and seed the historical data:
```bash
python set_admin_password.py
python seed_tickets.py
```

### 4. Run the Server
```bash
python main.py
```
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🛡️ Admin Access
To access the Admin Dashboard:
1. Navigate to the **Admin** tab in the web portal.
2. Enter the password created during the `set_admin_password.py` step.
3. You can now view all **Tickets**, the **Audit Trail**, and the **Knowledge Base**.
