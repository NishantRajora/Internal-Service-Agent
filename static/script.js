const API_BASE = "/api";

async function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    const section = document.getElementById(`${tab}-section`);
    if (section) section.classList.add('active');

    const btn = document.getElementById(`btn-${tab}`);
    if (btn) btn.classList.add('active');

    // Hide the employee logout button when admin view is active, show otherwise
    const logoutUserBtn = document.getElementById('logout-user');
    if (logoutUserBtn) {
        if (tab === 'admin') {
            logoutUserBtn.style.display = 'none';
        } else {
            logoutUserBtn.style.display = 'inline-block';
        }
    }

}

async function appendMessage(sender, text) {
    const chatBox = document.getElementById('chatBox');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    msgDiv.innerHTML = text.replace(/\\n/g, '<br>');
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendRequest() {
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    const request = document.getElementById('userRequest').value;

    if (!name || !email || !request) {
        alert("Please fill in all fields");
        return;
    }

    appendMessage('user', request);
    document.getElementById('userRequest').value = '';

    try {
        const response = await fetch(`${API_BASE}/support/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ employee_name: name, employee_email: email, request: request })
        });

        const data = await response.json();
        if (response.ok) {
            // Show the AI's response
            appendMessage('ai', data.response);
            // If a ticket was created, inform the user and refresh My Tickets
            if (data.ticket && data.ticket.ticket_id) {
                const ticketMsg = `✅ Ticket ${data.ticket.ticket_id} has been created and will appear in your tickets.`;
                appendMessage('ai', ticketMsg);
                // Preload tickets list (for when the user opens My Tickets)
                loadMyTickets();
            }
        } else {
            appendMessage('ai', `Error: ${data.detail || 'Something went wrong'}`);
        }
    } catch (e) {
        appendMessage('ai', "Connection error. Is the server running?");
    }
}

async function loadMyTickets() {
    const email = document.getElementById('userEmail').value;
    const listDiv = document.getElementById('myTicketsList');

    if (!email) {
        listDiv.innerHTML = '<p class="empty-msg">Please enter your email in the Support tab to view your tickets.</p>';
        return;
    }

    listDiv.innerHTML = 'Loading...';

    try {
        const response = await fetch(`${API_BASE}/support/my-tickets?email=${encodeURIComponent(email)}`);
        const tickets = await response.json();

        if (tickets.length === 0) {
            listDiv.innerHTML = '<p class="empty-msg">No tickets found for this email.</p>';
            return;
        }

        let html = '<div class="tickets-grid">';
        tickets.forEach(t => {
            const statusClass = `badge-${t.status.toLowerCase().split(' ')[0]}`;
            html += `
                <div class="ticket-card">
                    <div class="ticket-header">
                        <strong>${t.ticket_id}</strong>
                        <span class="badge ${statusClass}">${t.status}</span>
                    </div>
                    <p class="ticket-issue">${t.issue}</p>
                    <div class="ticket-footer">
                        <span>${t.category}</span> | <span>${t.action}</span>
                    </div>
                </div>`;
        });
        html += '</div>';
        listDiv.innerHTML = html;
    } catch (e) {
        listDiv.innerHTML = '<p class="error-msg">Error loading tickets.</p>';
    }
}

// Admin Logic
let adminToken = null;

async function loginAdmin() {
    const password = document.getElementById('adminPass').value;

    try {
        const response = await fetch(`${API_BASE}/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        if (response.ok) {
            const data = await response.json();
            adminToken = data.token;

            // Update header to indicate Admin mode
            document.getElementById('displayUserName').innerText = "🛡️ Admin Portal";

            document.getElementById('admin-login').style.display = 'none';
            document.getElementById('admin-dashboard').style.display = 'block';
            loadAdminTab('tickets');
        } else {
            alert("Invalid Admin Password");
        }
    } catch (e) {
        alert("Error connecting to server");
    }
}

function logoutAdmin() {
    adminToken = null;

    // Hide the main application and show the onboarding screen again
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';

    // Reset the admin login state within the app
    document.getElementById('admin-login').style.display = 'block';
    document.getElementById('admin-dashboard').style.display = 'none';
}
function logoutUser() {
    // Clear user session fields
    document.getElementById('userName').value = '';
    document.getElementById('userEmail').value = '';
    document.getElementById('displayUserName').innerText = 'Veridian IT Support';
    // Hide main app, show login screen
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';
    // Reset onboarding inputs
    document.getElementById('loginName').value = '';
    document.getElementById('loginEmail').value = '';
}

async function loadAdminTab(tab) {
    document.querySelectorAll('.admin-tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');

    const content = document.getElementById('admin-content');
    content.innerHTML = 'Loading...';

    try {
        const response = await fetch(`${API_BASE}/support/${tab}`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });

        if (!response.ok) throw new Error("Unauthorized");
        const data = await response.json();

        if (tab === 'tickets') {
            let html = `<table><thead><tr><th>ID</th><th>Employee</th><th>Issue</th><th>Status</th><th>Action</th><th>Manage</th></tr></thead><tbody>`;
            data.forEach(t => {
                const statusClass = `badge-${t.status.toLowerCase().split(' ')[0]}`;
                html += `<tr>
                    <td>${t.ticket_id}</td>
                    <td>${t.employee}</td>
                    <td>${t.issue}</td>
                    <td><span class="badge ${statusClass}">${t.status}</span></td>
                    <td>${t.action}</td>
                    <td><button onclick="updateTicketStatus('${t.ticket_id}')" class="admin-btn">Update Status</button></td>
                </tr>`;
            });
            html += `</tbody></table>`;
            content.innerHTML = html;
        } else if (tab === 'audit') {
            let html = `<table><thead><tr><th>Timestamp</th><th>Action</th><th>Details</th></tr></thead><tbody>`;
            data.forEach(l => {
                html += `<tr><td>${l.timestamp}</td><td>${l.action}</td><td><pre style="font-size:10px">${JSON.stringify(l.details, null, 2)}</pre></td></tr>`;
            });
            html += `</tbody></table>`;
            content.innerHTML = html;
        } else if (tab === 'policies') {
            let html = `<table><thead><tr><th>ID</th><th>Title</th><th>Description</th></tr></thead><tbody>`;
            data.forEach(p => {
                html += `<tr><td>${p.id}</td><td>${p.title}</td><td>${p.description}</td></tr>`;
            });
            html += `</tbody></table>`;
            content.innerHTML = html;
        }
    } catch (e) {
        content.innerHTML = `<p style="color:red">Error: ${e.message}</p>`;
    }
}

let currentUpdatingTicketId = null;

async function updateTicketStatus(ticketId) {
    currentUpdatingTicketId = ticketId;
    document.getElementById('modal-ticket-id').innerText = `Ticket: ${ticketId}`;
    document.getElementById('status-modal').style.display = 'flex';

    // Reset modal state
    document.getElementById('status-select').value = 'Resolved';
    document.getElementById('custom-status-container').style.display = 'none';
    document.getElementById('custom-status-input').value = '';
}

function closeStatusModal() {
    document.getElementById('status-modal').style.display = 'none';
    currentUpdatingTicketId = null;
}

async function submitStatusUpdate() {
    if (!currentUpdatingTicketId) return;

    const statusSelect = document.getElementById('status-select');
    let newStatus = statusSelect.value;

    if (newStatus === 'custom') {
        newStatus = document.getElementById('custom-status-input').value;
        if (!newStatus) {
            alert("Please enter a custom status");
            return;
        }
    }

    try {
        const response = await fetch(`${API_BASE}/support/tickets/${currentUpdatingTicketId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${adminToken}`
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            alert("Ticket updated successfully!");
            closeStatusModal();
            loadAdminTab('tickets');
        } else {
            const data = await response.json();
            alert(`Error: ${data.detail}`);
        }
    } catch (e) {
        alert("Connection error");
    }
}

// Initialize modal listener
document.addEventListener('DOMContentLoaded', () => {
    const statusSelect = document.getElementById('status-select');
    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            const container = document.getElementById('custom-status-container');
            if (container) {
                container.style.display = e.target.value === 'custom' ? 'block' : 'none';
            }
        });
    }
});


async function openAdminLogin() {
    // Skip the employee onboarding and go straight to admin portal
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';

    // Set a default generic user state since we are admins
    document.getElementById('userName').value = "Administrator";
    document.getElementById('userEmail').value = "admin@veridian-corp.example";
    document.getElementById('displayUserName').innerText = "🛡️ Admin Access Mode";

    showTab('admin');
}

async function handleUserLogin() {
    const name = document.getElementById('loginName').value;
    const email = document.getElementById('loginEmail').value;

    if (!name || !email) {
        alert("Please enter both your name and email to enter the portal.");
        return;
    }

    document.getElementById('userName').value = name;
    document.getElementById('userEmail').value = email;
    document.getElementById('displayUserName').innerText = `Welcome, ${name}!`;

    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';

    showTab('chat');
}

document.getElementById('sendBtn').onclick = sendRequest;
