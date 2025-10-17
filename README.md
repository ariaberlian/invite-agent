# Invitation Agent with Agent Development Kit (ADK)

An intelligent invitation assistant that can send invitations via multiple channels (email, WhatsApp) with calendar integration.

## Features

1. **Email Invitations** - Send invitations via email with calendar attachments (.ics)
2. **WhatsApp Invitations** - Send invitations via WhatsApp messages
3. **Calendar Integration** - Automatic calendar event generation
4. **Multi-user Support** - User authentication and session management
5. **Invitation Card Generator** *(coming soon)* - Generate invitation cards (image/web/pdf)

## Agent Workflow

The system uses a delegation architecture:

```
invitation_agent (main coordinator)
    ├── email_agent (handles email invitations)
    ├── whatsapp_agent (handles WhatsApp invitations)
    └── invitation_card_agent (generates invitation cards - coming soon)
```

## Architecture

The application consists of 5 microservices:

1. **PostgreSQL Database** - Stores user data, sessions, and invitation history
2. **WhatsApp Bridge (Go)** - Connects to WhatsApp Web API
3. **WhatsApp MCP Server (Python)** - MCP interface for WhatsApp operations
4. **Backend API (FastAPI)** - Main business logic and API endpoints
5. **Frontend (Gradio)** - User interface

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Go 1.16+ (for WhatsApp Bridge)
- Google Gemini API key
- Gmail account with App Password (for email invitations)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd invite-agent
```

### 2. Configure Environment Variables

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit [.env](.env) and configure:

- `DB_URL` - PostgreSQL connection string (e.g., `postgresql://username:password@localhost:5432/invitation_agent`)
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `EMAIL_HOST_USER` - Your Gmail address
- `EMAIL_HOST_PASSWORD` - Your Gmail App Password (not regular password)
- `SECRET_KEY` - Change to a secure random string for production
- `BACKEND_PORT` - Backend API port (default: 8000)
- `FRONTEND_PORT` - Frontend UI port (default: 8001)

### 3. Set Up PostgreSQL Database

Create a PostgreSQL database for the application:

```bash
psql -U postgres
CREATE DATABASE invitation_agent;
\q
```

Update the `DB_URL` in your [.env](.env) file with the correct credentials.

### 4. Install Python Dependencies

Using uv (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -e .
```

## Running the Services

You need to run **4 separate services** in different terminals. Open 4 terminal windows and run each service:

### Terminal 1: Backend API

The backend API handles all business logic, authentication, and agent orchestration.

```bash
# From the project root
uv run python backend.py
```

or

```bash
python backend.py
```

The backend will start on [http://localhost:8001](http://localhost:8001)

### Terminal 2: Frontend UI

The Gradio frontend provides a user-friendly chat interface.

```bash
# From the project root
uv run python frontend.py
```

or

```bash
python frontend.py
```

The frontend will start on [http://localhost:8002](http://localhost:8002)

### Terminal 3: WhatsApp Bridge (Go)

The WhatsApp bridge connects to WhatsApp Web and exposes a REST API.

```bash
# Navigate to the WhatsApp bridge directory
cd whatsapp-mcp/whatsapp-bridge

# Run the Go application
go run main.go
```

**First-time setup:** On first run, you'll see a QR code in the terminal. Scan it with your WhatsApp mobile app (Settings > Linked Devices > Link a Device) to authenticate.

The bridge will start on [http://localhost:8080](http://localhost:8080)

### Terminal 4: WhatsApp MCP Server

The WhatsApp MCP server provides the Model Context Protocol interface for WhatsApp operations.

```bash
# Navigate to the MCP server directory
cd whatsapp-mcp/whatsapp-mcp-server

# Install dependencies
uv sync

# Run the MCP server
uv run python main.py
```

or

```bash
cd whatsapp-mcp/whatsapp-mcp-server
python main.py
```
The MCP server will start on [http://localhost:8000](http://localhost:8000)

## Service Overview

| Service | Port | Purpose | Required |
|---------|------|---------|----------|
| Backend API | 8001 | Business logic, authentication, agent coordination | Yes |
| Frontend UI | 8002 | User interface | Yes |
| WhatsApp Bridge | 8080 | WhatsApp Web connection | For WhatsApp features |
| WhatsApp MCP Server | 8000 | MCP protocol interface | For WhatsApp features |
| PostgreSQL | 5432 | Database storage | Yes |

## Usage

1. Open your browser and navigate to [http://localhost:8002](http://localhost:8002)
2. Register a new account or login with existing credentials
3. Start chatting with the invitation assistant
4. The agent will help you:
   - Create invitation details (event name, date, time, location, etc.)
   - Send invitations via email with calendar attachments
   - Send invitations via WhatsApp messages
   - Manage multiple invitation sessions

### Example Conversation

```
You: I need to send an invitation for my birthday party
Agent: I'd be happy to help you send invitations! Let me gather the details...
      What is the name of the event?

You: John's 30th Birthday Party
Agent: Great! When is the party?

You: December 25th, 2025 at 7 PM
Agent: Perfect! Where will the party be held?

You: 123 Main Street, New York
...
```

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `systemctl status postgresql` (Linux) or check Services (Windows)
- Verify database exists: `psql -U postgres -l`
- Check `DB_URL` format in [.env](.env)

### WhatsApp Connection Issues

- Make sure the WhatsApp Bridge is running and showing "Connected to WhatsApp"
- Re-scan QR code if connection is lost
- Check that WhatsApp Web is not open in another browser (only one connection allowed)

### Email Sending Issues

- Verify you're using a Gmail App Password, not your regular password
- Enable 2-factor authentication on your Google account
- Generate App Password at: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### Port Conflicts

If default ports are in use, update these in [.env](.env):

- `BACKEND_PORT` - Change backend port
- `FRONTEND_PORT` - Change frontend port

## Development

### Project Structure

```
invite-agent/
├── invitation_agent/          # Main agent logic
│   ├── agent.py              # Root agent
│   └── sub_agents/           # Delegated sub-agents
│       ├── email_agent/      # Email invitation handler
│       └── whatsapp_agent/   # WhatsApp invitation handler
├── auth/                     # Authentication & user management
├── shared/                   # Shared models and schemas
├── utils/                    # Utility functions
├── whatsapp-mcp/            # WhatsApp integration
│   ├── whatsapp-bridge/     # Go service for WhatsApp Web
│   └── whatsapp-mcp-server/ # Python MCP server
├── backend.py               # FastAPI backend server
├── frontend.py              # Gradio frontend UI
├── config.py                # Configuration management
└── .env                     # Environment variables
```

## License

See [LICENSE](LICENSE) for details.