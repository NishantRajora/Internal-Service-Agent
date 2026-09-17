import json
import requests
import os
from dotenv import load_dotenv
from retriever import find_relevant_policy
from database import create_ticket, add_audit_log, get_all_tickets
from auth_utils import verify_password

# Load environment variables
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip('/')
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Construct the final endpoint
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"

# ============================================================
# OLLAMA API HELPER
# ============================================================
def call_ollama(prompt, system_prompt="You are a helpful AI assistant."):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json" if "json" in system_prompt.lower() else ""
    }
    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama Error: {e}")
        return None

# ============================================================
# LLM-BASED CLASSIFICATION
# ============================================================
def classify_request(request):
    categories = [
        "Security Incident", "Account Access", "VPN Access",
        "Laptop / Hardware", "Software Installation", "Printer",
        "Email / Mailbox", "Guest Wi-Fi", "Expense Software",
        "Home Office Equipment", "Admin / Server Access", "Unknown"
    ]
    system_prompt = (
        f"You are an IT support classifier for Veridian Corp. "
        f"Classify the user's request into exactly one of these categories: {categories}. "
        "Return only the category name. If unsure, return 'Unknown'. "
        "Return result as JSON: {\"category\": \"category_name\"}"
    )
    prompt = f"User Request: {request}"
    result = call_ollama(prompt, system_prompt)
    if result:
        try:
            data = json.loads(result)
            return data.get("category", "Unknown")
        except:
            pass
    return "Unknown"

# ============================================================
# LLM-BASED DECISION MAKING
# ============================================================
def make_decision(category, request, policy, historical_context=""):
    policy_text = policy.get("description", "No policy available") if policy else "No policy available"
    policy_id = policy.get("id", "N/A") if policy else "N/A"

    system_prompt = (
        "You are the Decision Engine for Veridian Corp IT Support. "
        "Your goal is to determine the correct action based ONLY on the provided policy. "
        "However, you should use the provided Historical Precedents to ensure consistency. "
        "If a similar request was rejected or approved in the past, follow that pattern. "
        "Do not invent rules. "
        "Return a JSON object with the following keys:\n"
        "- status: 'Resolved', 'Escalated', or 'Follow-up Required'\n"
        "- action: A short description of the action to be taken\n"
        "- needs_ticket: boolean (True if human intervention/IT work is required)\n"
        "- reason: A brief explanation of why this decision was made based on the policy and past cases\n"
        "- follow_up: A question to ask the user if status is 'Follow-up Required', otherwise null"
    )

    prompt = (
        f"Category: {category}\n"
        f"Policy ID: {policy_id}\n"
        f"Policy Content: {policy_text}\n\n"
        f"Historical Precedents: {historical_context}\n\n"
        f"User Request: {request}\n\n"
        "Decision:"
    )

    result = call_ollama(prompt, system_prompt)
    if result:
        try:
            return json.loads(result)
        except:
            pass

    return {
        "status": "Follow-up Required",
        "action": "Request clarification",
        "needs_ticket": False,
        "reason": "LLM decision failed, requesting clarification for safety.",
        "follow_up": "Could you please provide more details about your issue?"
    }

# ============================================================
# LLM-BASED RESPONSE GENERATION
# ============================================================
def generate_response(employee_name, request, category, policy, decision, ticket):
    policy_id = policy.get("id", "N/A")
    policy_title = policy.get("title", "Unknown")
    policy_text = policy.get("description", "")

    system_prompt = (
        "You are a polite and professional IT Support Agent at Veridian Corp. "
        "Write a response to the employee based on the provided decision and policy. "
        "Be clear, concise, and empathetic. "
        "Always mention the policy source."
    )

    prompt = (
        f"Employee: {employee_name}\n"
        f"Request: {request}\n"
        f"Category: {category}\n"
        f"Decision Status: {decision['status']}\n"
        f"Decision Action: {decision['action']}\n"
        f"Decision Reason: {decision['reason']}\n"
        f"Policy: {policy_id} - {policy_title}: {policy_text}\n"
        f"Ticket: {ticket['ticket_id'] if ticket else 'None'}\n\n"
        "Response:"
    )

    result = call_ollama(prompt, system_prompt)
    if result:
        return result

    return "I'm sorry, I encountered an error generating the response. Please contact IT support directly."

# ============================================================
# MAIN AGENT WORKFLOW
# ============================================================
def process_request(employee_name, employee_email, request):
    # 1. Classify request
    category = classify_request(request)

    # 2. Retrieve relevant policy
    policy = find_relevant_policy(category=category, request=request)

    # Convert policy to a simple dict for the LLM
    policy_info = {
        "id": policy.get("id", "N/A") if policy else "N/A",
        "title": policy.get("title", "No policy found") if policy else "No policy found",
        "description": policy.get("description", "") if policy else ""
    }

    # 3. Fetch historical precedents
    all_tickets = get_all_tickets()
    # Filter tickets of the same category to provide as context
    relevant_precedents = [
        f"Ticket {t['ticket_id']}: {t['issue']} -> {t['status']} ({t['action']})"
        for t in all_tickets if t.get('category') == category
    ]
    historical_context = "\n".join(relevant_precedents) if relevant_precedents else "No prior cases found."

    # 4. Make decision
    decision = make_decision(category, request, policy, historical_context)

    # 5. Create ticket if required
    ticket = None
    if decision.get("needs_ticket"):
        ticket = create_ticket(
            employee=employee_name,
            email=employee_email,
            issue=request,
            category=category,
            action=decision.get("action", "IT Review"),
            policy_id=policy_info["id"],
            status=decision.get("status", "Escalated")
        )

    # 6. Generate employee response
    response = generate_response(
        employee_name=employee_name,
        request=request,
        category=category,
        policy=policy_info,
        decision=decision,
        ticket=ticket
    )

    # 7. Audit log
    audit_data = {
        "employee": employee_name,
        "email": employee_email,
        "request": request,
        "category": category,
        "policy_id": policy_info["id"],
        "policy_title": policy_info["title"],
        "decision": decision.get("action"),
        "status": decision.get("status"),
        "ticket_id": ticket.get("ticket_id") if ticket else None
    }
    add_audit_log(
        action=decision.get("action", "Processed"),
        details=audit_data
    )

    return {
        "status": decision.get("status", "Unknown"),
        "response": response,
        "category": category,
        "action": decision.get("action", "Unknown"),
        "policy_id": policy_info["id"],
        "policy_title": policy_info["title"],
        "policy_text": policy_info["description"],
        "follow_up_question": decision.get("follow_up"),
        "ticket": ticket
    }
