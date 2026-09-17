const API_BASE = "/api";

async function handleUserLogin() {
    const name = document.getElementById('loginName').value;
    const email = document.getElementById('loginEmail').value;

    if (!name || !email) {
        alert("Please enter both your name and email to enter the portal.");
        return;
    }

    // Store user info in local state
    document.getElementById('userName').value = name;
    document.getElementById('userEmail').value = email;
    document.getElementById('displayUserName').innerText = `Welcome, ${name}!`;

    // Switch screens
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';

    // Load initial data
    showTab('chat');
}

async function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    const section = document.getElementById(`${tab}-section`);
    if (section) section.classList.add('active');

    const btn = document.getElementById(`btn-${tab}`);
    if (btn) btn.classList.add('active');

    if (tab === 'my-tickets') {
        loadMyTickets();
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
            appendMessage('ai', data.response);
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
    document.getElementById('admin-login').style.display = 'block';
    document.getElementById('admin-dashboard').style.display = 'none';
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
            let html = `<table><thead><tr><th>ID</th><th>Employee</th><th>Issue</th><th>Status</th><th>Action</th></tr></thead><tbody>`;
            data.forEach(t => {
                const statusClass = `badge-${t.status.toLowerCase().split(' ')[0]}`;
                html += `<tr><td>${t.ticket_id}</td><td>${t.employee}</td><td>${t.issue}</td><td><span class="badge ${statusClass}">${t.status}</span></td><td>${t.action}</td></tr>`;
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

document.getElementById('sendBtn').onclick = sendRequest;
