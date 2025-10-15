from google.adk.agents.llm_agent import Agent
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams



TARGET_FOLDER_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "whatsapp-mcp", "whatsapp-mcp-server"))

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='An agent to send whatsapp messages.',
    instruction="""
    You are a whatsapp broadcaster agent. You compose a message and send it by user request.

""",
    tools=[
        # MCPToolset(
        #     connection_params=StdioConnectionParams(
        #         server_params = StdioServerParameters(
        #             command=r'C:\Users\aria\.local\bin\uv.exe',
        #             args=[
        #                 "--directory",
        #                 TARGET_FOLDER_PATH,
        #                 "run",
        #                 "main.py"
        #             ],
        #         ),
        #         timeout=300.0,  # 5 minutes timeout instead of default 5 seconds
        #     ),
        # )

        MCPToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:8000/sse",
                timeout=5.0,
                sse_read_timeout=300.0,
            ),
            tool_filter=['search_contacts', 'send_messages']
        
        )
    ],
)

