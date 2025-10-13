import gradio as gr
import requests
from typing import Optional, Tuple

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
    return [], "", "Logged out successfully"

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

def reset_conversation():
    """Reset conversation"""
    auth_state["session_id"] = None
    return [], ""

def check_backend_health() -> str:
    """Check backend health"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return "🟢 Backend is healthy"
        else:
            return f"🔴 Backend returned status {response.status_code}"
    except Exception as e:
        return f"🔴 Backend is not reachable: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Invitation Assistant", theme=gr.themes.Soft()) as demo:

    # Login/Register Section (visible by default)
    with gr.Column(visible=True) as auth_section:
        with gr.Tabs():
            # Login Tab
            with gr.Tab("Login"):
                gr.Markdown("# 🔐 Login")
                login_username = gr.Textbox(label="Username", placeholder="Enter username")
                login_password = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                login_button = gr.Button("Login", variant="primary")
                login_message = gr.Textbox(label="Status", interactive=False)

            # Register Tab
            with gr.Tab("Register"):
                gr.Markdown("# 📝 Create Account")
                reg_username = gr.Textbox(label="Username", placeholder="Enter username")
                reg_full_name = gr.Textbox(label="Full Name", placeholder="Enter your full name")
                reg_email = gr.Textbox(label="Email", placeholder="Enter email")
                reg_password = gr.Textbox(label="Password", type="password", placeholder="Enter password (min 6 characters)")
                reg_confirm_password = gr.Textbox(label="Confirm Password", type="password", placeholder="Confirm password")
                reg_button = gr.Button("Register", variant="primary")
                reg_message = gr.Textbox(label="Status", interactive=False)

    # Chat Section (hidden until login)
    with gr.Column(visible=False) as chat_section:
        # User info header
        with gr.Row():
            user_info = gr.Markdown("", visible=False)
            logout_button = gr.Button("🚪 Logout", variant="secondary", scale=0)

        gr.Markdown(
            """
            # 📧 Invitation Assistant

            Your AI-powered assistant for creating and managing event invitations.

            **How to use:**
            1. Start a conversation by describing your invitation needs
            2. The assistant will help you create invitations and send emails
            3. Use the "New Conversation" button to start fresh
            """
        )

        # Health status
        with gr.Row():
            health_status = gr.Textbox(
                label="Backend Status",
                value=check_backend_health(),
                interactive=False,
                scale=3
            )
            refresh_btn = gr.Button("🔄 Refresh", scale=1)

        # Chat interface
        chatbot = gr.Chatbot(
            label="Chat with Invitation Assistant",
            height=500,
            show_label=True,
            autoscroll=True,
            type='messages',
        )

        with gr.Row():
            msg = gr.Textbox(
                label="Your message",
                placeholder="Type your message here...",
                lines=2,
                scale=4
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat")
            new_conv_btn = gr.Button("🆕 New Conversation", variant="secondary")

    # Hidden state to manage tab visibility
    chat_visible = gr.State(False)

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
            user_display = f"👤 **{user_data['full_name']}** (@{user_data['username']})"
            # Hide auth section, show chat section
            return (
                msg,  # login_message
                gr.update(visible=False),  # auth_section
                gr.update(visible=True),   # chat_section
                gr.update(value=user_display, visible=True),  # user_info
            )
        else:
            return (
                msg,  # login_message
                gr.update(visible=True),   # auth_section
                gr.update(visible=False),  # chat_section
                gr.update(visible=False),  # user_info
            )

    login_button.click(
        fn=handle_login,
        inputs=[login_username, login_password],
        outputs=[login_message, auth_section, chat_section, user_info]
    )

    # Logout handler
    def handle_logout():
        chatbot_clear, msg_clear, logout_msg = logout_user()
        return (
            logout_msg,  # login_message
            gr.update(visible=True),   # auth_section
            gr.update(visible=False),  # chat_section
            gr.update(visible=False),  # user_info
            chatbot_clear,  # chatbot
            msg_clear,  # msg
        )

    logout_button.click(
        fn=handle_logout,
        outputs=[login_message, auth_section, chat_section, user_info, chatbot, msg]
    )

    # Chat handlers
    msg.submit(
        fn=chat_with_agent,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )

    send_btn.click(
        fn=chat_with_agent,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )

    clear_btn.click(
        fn=lambda: ([], ""),
        outputs=[chatbot, msg]
    )

    new_conv_btn.click(
        fn=reset_conversation,
        outputs=[chatbot, msg]
    )

    refresh_btn.click(
        fn=check_backend_health,
        outputs=health_status
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
