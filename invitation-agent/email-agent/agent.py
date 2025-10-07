from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='An Email Agent to Create Email, Send Email, and Read Email Replies',
    instruction="""


""",
    tools=[
    ],
    
)
