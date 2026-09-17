from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets

from agent import process_request
from database import get_all_tickets, get_audit_logs, get_setting, get_ticket
from retriever import load_policies
from auth_utils import verify_password

app = FastAPI(
    title="Veridian Corp AI IT Support",
    description="Integrated IT Support system with AI Agent and Admin Dashboard",
    version="2.0.0"
)

# ============================================================
# STATIC FILES
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# ============================================================
# MODELS
# ============================================================

class SupportRequest(BaseModel):
    employee_name: str
    employee_email: EmailStr
    request: str

class LoginRequest(BaseModel):
    password: str

class TicketUpdate(BaseModel):
    status: str

# ============================================================
# AUTHENTICATION
# ============================================================

# Simple in-memory token store for the prototype
SESSION_TOKENS = {}

async def verify_admin_token(authorization: Optional[str] = Header(None)):
    """Dependency to protect admin endpoints."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: Missing or invalid token")

    token = authorization.split(" ")[1]
    if token not in SESSION_TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized: Session expired or invalid")

    return True

# ============================================================
# API ENDPOINTS
# ============================================================

@app.post("/api/admin/login")
async def login(req: LoginRequest):
    """
    Authenticate admin and return a temporary session token.
    """
    hashed_password = get_setting("admin_password")
    if not hashed_password:
        raise HTTPException(status_code=500, detail="Admin password not set. Run set_admin_password.py first.")

    if verify_password(req.password, hashed_password):
        token = secrets.token_hex(32)
        SESSION_TOKENS[token] = True
        return {"token": token}

    raise HTTPException(status_code=401, detail="Invalid password")

@app.post("/api/support/request")
async def handle_request(req: SupportRequest):
    """
    Submit an IT support request to the AI Agent.
    """
    try:
        result = process_request(
            employee_name=req.employee_name,
            employee_email=req.employee_email,
            request=req.request
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/api/support/my-tickets")
async def get_my_tickets(email: str):
    """
    Retrieve tickets for a specific employee.
    """
    try:
        all_tickets = get_all_tickets()
        user_tickets = [t for t in all_tickets if t.get("email") == email]
        return user_tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/support/tickets", dependencies=[Depends(verify_admin_token)])
async def list_tickets():
    """
    Retrieve all IT support tickets (Admin only).
    """
    try:
        return get_all_tickets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.patch("/api/support/tickets/{ticket_id}", dependencies=[Depends(verify_admin_token)])
async def update_ticket(ticket_id: str, update: TicketUpdate):
    """
    Update ticket status (Admin only).
    """
    from database import update_ticket_status
    try:
        success = update_ticket_status(ticket_id, update.status)
        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {"message": "Ticket updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/support/audit", dependencies=[Depends(verify_admin_token)])
async def list_audit_logs():
    """
    Retrieve the complete audit trail (Admin only).
    """
    try:
        return get_audit_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/support/policies", dependencies=[Depends(verify_admin_token)])
async def list_policies():
    """
    Retrieve company knowledge base policies (Admin only).
    """
    try:
        return load_policies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
