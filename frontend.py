import gradio as gr
import requests
import logging
from typing import Optional, Tuple
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)

# Backend configuration
BACKEND_URL = "http://localhost:8000"

# Global state for authentication and session
auth_state = {
    "token": None,
    "user": None,
    "session_id": None
}

def register_user(username: str, full_name: str, email: str, password: str, confirm_password: str) -> Tuple[str, bool]:
    """Register a new user"""
    if not username or not full_name or not email or not password:
        return "❌ All fields are required", False

    if password != confirm_password:
        return "❌ Passwords do not match", False

    if len(password) < 6:
        return "❌ Password must be at least 6 characters", False

    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "username": username,
                "full_name": full_name,
                "email": email,
                "password": password
            },
            timeout=10
        )

        if response.status_code == 201:
            return f"✅ Registration successful! Please login with username: {username}", True
        else:
            error = response.json().get("detail", "Unknown error")
            return f"❌ Registration failed: {error}", False

    except Exception as e:
        return f"❌ Error: {str(e)}", False

def login_user(username: str, password: str) -> Tuple[str, bool, dict]:
    """Login user and get token"""
    if not username or not password:
        return "❌ Username and password are required", False, {}

    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]

            # Get user info
            user_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            if user_response.status_code == 200:
                user_data = user_response.json()
                auth_state["token"] = token
                auth_state["user"] = user_data
                auth_state["session_id"] = None

                return f"✅ Welcome, {user_data['full_name']}!", True, user_data
            else:
                return "❌ Failed to get user info", False, {}
        else:
            error = response.json().get("detail", "Invalid credentials")
            return f"❌ Login failed: {error}", False, {}

    except Exception as e:
        return f"❌ Error: {str(e)}", False, {}

def logout_user():
    """Logout user"""
    auth_state["token"] = None
    auth_state["user"] = None
    auth_state["session_id"] = None
    return []

def chat_with_agent(message: str, history: list) -> Tuple[list, str]:
    """Send message to backend with authentication"""
    if not message.strip():
        return history, ""

    if not auth_state["token"]:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "❌ Not authenticated. Please login."})
        return history, ""

    try:
        payload = {
            "message": message,
            "session_id": auth_state["session_id"]
        }

        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            headers={"Authorization": f"Bearer {auth_state['token']}"},
            timeout=60
        )

        if response.status_code == 401:
            auth_state["token"] = None
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": "❌ Session expired. Please login again."})
            return history, ""

        response.raise_for_status()
        data = response.json()
        assistant_message = data["response"]
        auth_state["session_id"] = data["session_id"]

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": assistant_message})

    except requests.exceptions.RequestException as e:
        error_msg = f"Error: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})

    return history, ""

def load_sessions() -> list:
    """Load all sessions for the authenticated user"""
    if not auth_state["token"]:
        return []

    try:
        response = requests.get(
            f"{BACKEND_URL}/sessions",
            headers={"Authorization": f"Bearer {auth_state['token']}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", [])
            return sessions
        else:
            return []

    except Exception as e:
        logger.error(f"Error loading sessions: {str(e)}")
        return []

def load_chat_history(session_id: str) -> list:
    """Load chat history for a specific session"""
    if not auth_state["token"] or not session_id:
        return []

    try:
        response = requests.get(
            f"{BACKEND_URL}/sessions/{session_id}/history",
            headers={"Authorization": f"Bearer {auth_state['token']}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])

            # Convert messages to the format expected by Gradio chatbot
            history = []
            for msg in messages:
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            return history
        else:
            logger.error(f"Failed to load chat history: {response.status_code}")
            return []

    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return []

def delete_session(session_id: str) -> bool:
    """Delete a specific session"""
    if not auth_state["token"] or not session_id:
        return False

    try:
        response = requests.delete(
            f"{BACKEND_URL}/sessions/{session_id}",
            headers={"Authorization": f"Bearer {auth_state['token']}"},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        return False

def format_session_for_display(session):
    """Format a single session for display"""
    preview = session.get("preview") or "New conversation"
    created_at = session.get("created_at", "")

    try:
        dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
        time_str = dt.strftime("%b %d, %H:%M")
    except:
        time_str = ""

    return f"{preview[:35]}\n{time_str}"

# Create Gradio interface
with gr.Blocks(title="Invitation Assistant", theme=gr.themes.Soft()) as demo:

    # State
    sessions_state = gr.State([])

    # Login/Register Section
    with gr.Column(visible=True) as auth_section:
        with gr.Tabs():
            with gr.Tab("Login"):
                gr.Markdown("# 🔐 Login")
                login_username = gr.Textbox(label="Username", placeholder="Enter username")
                login_password = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                login_button = gr.Button("Login", variant="primary")
                login_message = gr.Textbox(label="Status", interactive=False)

            with gr.Tab("Register"):
                gr.Markdown("# 📝 Create Account")
                reg_username = gr.Textbox(label="Username", placeholder="Enter username")
                reg_full_name = gr.Textbox(label="Full Name", placeholder="Enter your full name")
                reg_email = gr.Textbox(label="Email", placeholder="Enter email")
                reg_password = gr.Textbox(label="Password", type="password", placeholder="Enter password (min 6 characters)")
                reg_confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Confirm password")
                reg_button = gr.Button("Register", variant="primary")
                reg_message = gr.Textbox(label="Status", interactive=False)

    # Chat Section with Sidebar
    with gr.Row(visible=False) as chat_section:
        # Sidebar
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("## 📧 Chats")
            user_info = gr.Markdown("")

            new_chat_btn = gr.Button("➕ New Chat", variant="primary")
            refresh_sessions_btn = gr.Button("🔄 Refresh", size="sm")

            gr.Markdown("---")

            # Sessions list as radio buttons
            sessions_radio = gr.Radio(
                choices=[],
                label="Conversations",
                interactive=True
            )

            delete_session_btn = gr.Button("🗑️ Delete Selected", size="sm", variant="stop")

            gr.Markdown("---")
            logout_button = gr.Button("🚪 Logout", size="sm")

        # Main Chat Area
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Invitation Assistant",
                height=600,
                type='messages'
            )

            with gr.Row():
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    lines=2,
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

    # Register handler
    def handle_register(username, full_name, email, password, confirm_password):
        msg, success = register_user(username, full_name, email, password, confirm_password)
        return msg

    reg_button.click(
        fn=handle_register,
        inputs=[reg_username, reg_full_name, reg_email, reg_password, reg_confirm_password],
        outputs=reg_message
    )

    # Login handler
    def handle_login(username, password):
        msg, success, user_data = login_user(username, password)

        if success:
            sessions = load_sessions()
            session_choices = [(format_session_for_display(s), s['session_id']) for s in sessions]
            user_display = f"**{user_data['full_name']}**\n@{user_data['username']}"

            return (
                msg,
                gr.update(visible=False),  # auth_section
                gr.update(visible=True),   # chat_section
                user_display,
                sessions,
                gr.update(choices=session_choices, value=None)
            )
        else:
            return (
                msg,
                gr.update(visible=True),
                gr.update(visible=False),
                "",
                [],
                gr.update(choices=[])
            )

    login_button.click(
        fn=handle_login,
        inputs=[login_username, login_password],
        outputs=[login_message, auth_section, chat_section, user_info, sessions_state, sessions_radio]
    )

    # Logout handler
    def handle_logout():
        logout_user()
        return (
            "Logged out",
            gr.update(visible=True),
            gr.update(visible=False),
            "",
            [],
            [],
            gr.update(choices=[])
        )

    logout_button.click(
        fn=handle_logout,
        outputs=[login_message, auth_section, chat_section, user_info, chatbot, sessions_state, sessions_radio]
    )

    # New chat handler
    def handle_new_chat():
        auth_state["session_id"] = None
        return [], ""

    new_chat_btn.click(
        fn=handle_new_chat,
        outputs=[chatbot, msg]
    )

    # Refresh sessions handler
    def handle_refresh_sessions(current_sessions):
        sessions = load_sessions()
        session_choices = [(format_session_for_display(s), s['session_id']) for s in sessions]
        return sessions, gr.update(choices=session_choices, value=None)

    refresh_sessions_btn.click(
        fn=handle_refresh_sessions,
        inputs=[sessions_state],
        outputs=[sessions_state, sessions_radio]
    )

    # Load session when selected
    def handle_session_select(session_id, sessions):
        if session_id:
            auth_state["session_id"] = session_id
            # Load chat history from the backend
            history = load_chat_history(session_id)
            return history, ""
        return [], ""

    sessions_radio.change(
        fn=handle_session_select,
        inputs=[sessions_radio, sessions_state],
        outputs=[chatbot, msg]
    )

    # Delete session handler
    def handle_delete_session(selected_session, sessions):
        if not selected_session:
            return sessions, gr.update(choices=[(format_session_for_display(s), s['session_id']) for s in sessions], value=None), []

        success = delete_session(selected_session)
        if success:
            # Refresh sessions
            new_sessions = load_sessions()
            session_choices = [(format_session_for_display(s), s['session_id']) for s in new_sessions]

            # Clear chat if deleted session was active
            if auth_state.get("session_id") == selected_session:
                auth_state["session_id"] = None
                return new_sessions, gr.update(choices=session_choices, value=None), []

            return new_sessions, gr.update(choices=session_choices, value=None), []

        return sessions, gr.update(), []

    delete_session_btn.click(
        fn=handle_delete_session,
        inputs=[sessions_radio, sessions_state],
        outputs=[sessions_state, sessions_radio, chatbot]
    )

    # Chat handlers
    def handle_chat(message, history, sessions):
        new_history, _ = chat_with_agent(message, history)

        # Refresh sessions to show new/updated session
        new_sessions = load_sessions()
        session_choices = [(format_session_for_display(s), s['session_id']) for s in new_sessions]

        return new_history, "", new_sessions, gr.update(choices=session_choices)

    msg.submit(
        fn=handle_chat,
        inputs=[msg, chatbot, sessions_state],
        outputs=[chatbot, msg, sessions_state, sessions_radio]
    )

    send_btn.click(
        fn=handle_chat,
        inputs=[msg, chatbot, sessions_state],
        outputs=[chatbot, msg, sessions_state, sessions_radio]
    )

    demo.css = "footer {visibility: hidden}"

if __name__ == "__main__":
    print("Starting Invitation Assistant Frontend...")
    print(f"Backend URL: {BACKEND_URL}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=8001,
        share=False
    )
