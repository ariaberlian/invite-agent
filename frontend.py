import gradio as gr
import requests
from typing import Optional

# Backend configuration
BACKEND_URL = "http://localhost:8000"
USER_ID = "budigalaksi123"

# Store session_id globally for the conversation
session_state = {"session_id": None}

def chat_with_agent(message: str, history: list) -> tuple:
    """
    Send message to backend and return response

    Args:
        message: User's message
        history: Chat history (Gradio format)

    Returns:
        Tuple of (updated history, empty string for clearing input)
    """
    if not message.strip():
        return history, ""

    try:
        # Prepare request
        payload = {
            "message": message,
            "user_id": USER_ID,
            "session_id": session_state["session_id"]
        }

        # Call backend
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        # Parse response
        data = response.json()
        assistant_message = data["response"]
        session_state["session_id"] = data["session_id"]

        # Update history
        history.append((message, assistant_message))

    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to backend: {str(e)}"
        history.append((message, error_msg))
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        history.append((message, error_msg))

    return history, ""

def reset_conversation():
    """Reset the conversation by clearing session"""
    session_state["session_id"] = None
    return [], ""

def check_backend_health() -> str:
    """Check if backend is healthy"""
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
        bubble_full_width=False
    )

    with gr.Row():
        msg = gr.Textbox(
            label="Your message",
            placeholder="Type your message here... (e.g., 'I want to create an invitation for a team meeting')",
            lines=2,
            scale=4
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    with gr.Row():
        clear_btn = gr.Button("🗑️ Clear Chat")
        new_conv_btn = gr.Button("🆕 New Conversation", variant="secondary")

    # Example prompts
    gr.Examples(
        examples=[
            "I want to create an invitation for a team meeting next Monday at 2 PM",
            "Help me invite people to my birthday party on December 25th",
            "Create a formal invitation for a business conference",
            "I need to send invites for a virtual workshop",
        ],
        inputs=msg,
        label="Example Prompts"
    )

    # Session info (hidden, for debugging)
    with gr.Accordion("Session Info (Debug)", open=False):
        session_info = gr.JSON(label="Current Session", value=session_state)

    # Event handlers
    msg.submit(
        fn=chat_with_agent,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    ).then(
        fn=lambda: session_state,
        outputs=session_info
    )

    send_btn.click(
        fn=chat_with_agent,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    ).then(
        fn=lambda: session_state,
        outputs=session_info
    )

    clear_btn.click(
        fn=lambda: ([], ""),
        outputs=[chatbot, msg]
    )

    new_conv_btn.click(
        fn=reset_conversation,
        outputs=[chatbot, msg]
    ).then(
        fn=lambda: session_state,
        outputs=session_info
    )

    refresh_btn.click(
        fn=check_backend_health,
        outputs=health_status
    )

if __name__ == "__main__":
    print("Starting Invitation Assistant Frontend...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"User ID: {USER_ID}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=8001,
        share=False
    )
