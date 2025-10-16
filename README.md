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

## Quick Start with Docker

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- WhatsApp account for scanning QR code

### 1. Setup Environment

Copy the environment template:

```bash
cp .env.docker .env
```

Edit `.env` and configure:

```bash
# Required: Google API key for AI features
GOOGLE_API_KEY=your-google-api-key

# Required: Email credentials (use App Password for Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Required: Change in production!
SECRET_KEY=your-secure-random-string
```

### 2. Start Services

```bash
docker-compose up -d --build
```

### 3. Authenticate WhatsApp

Watch the WhatsApp Bridge logs to see the QR code:

```bash
docker-compose logs -f whatsapp-bridge
```

Scan the QR code with your WhatsApp mobile app:
1. Open WhatsApp on your phone
2. Go to **Settings** > **Linked Devices**
3. Tap **Link a Device**
4. Scan the QR code shown in the terminal

### 4. Access Application

- **Frontend UI**: http://localhost:7860
- **API Documentation**: http://localhost:8000/docs (if exposed)

### 5. Create Account & Start Inviting

1. Open http://localhost:7860
2. Register a new account
3. Login with your credentials
4. Start creating invitations!

## Management Commands

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f whatsapp-bridge

# Stop all services
docker-compose down

# Stop and remove all data (WARNING: deletes database)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild specific service
docker-compose up --build -d backend
```

## Port Configuration

| Service | Port | Exposed | Description |
|---------|------|---------|-------------|
| PostgreSQL | 5432 | No | Database |
| WhatsApp Bridge | 8080 | Yes | For QR code scanning |
| WhatsApp MCP | 5000 | No | Internal MCP server |
| Backend API | 8000 | No | FastAPI backend |
| Frontend | 7860 | Yes | Gradio UI |

Only ports **7860** (Frontend) and **8080** (WhatsApp Bridge) are exposed to the host.

## Documentation

- [Complete Docker Guide](DOCKER.md) - Detailed Docker setup and troubleshooting
- [Environment Variables](.env.docker) - All available configuration options

## Development

For local development without Docker:

1. Install Python 3.12+ and Go 1.24+
2. Install PostgreSQL
3. Install dependencies: `uv pip install -e .`
4. Configure `.env` with local database URL
5. Run services individually:
   ```bash
   # Terminal 1: Database (already running)
   # Terminal 2: WhatsApp Bridge
   cd whatsapp-mcp/whatsapp-bridge && go run main.go

   # Terminal 3: WhatsApp MCP Server
   cd whatsapp-mcp/whatsapp-mcp-server && python main.py

   # Terminal 4: Backend
   python backend.py

   # Terminal 5: Frontend
   python frontend.py
   ```

## Troubleshooting

### Services won't start
```bash
docker-compose logs
```

### WhatsApp not connecting
```bash
docker-compose restart whatsapp-bridge
docker-compose logs -f whatsapp-bridge
```

### Database connection issues
```bash
# Check if PostgreSQL is ready
docker-compose logs postgres
```

For more troubleshooting, see [DOCKER.md](DOCKER.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

