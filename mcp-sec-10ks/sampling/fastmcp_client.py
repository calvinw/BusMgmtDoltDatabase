"""
Simple FastMCP Client - In-Memory Testing with Logging
"""
import asyncio
from fastmcp import Client
from fastmcp_server import mcp  # Import the server directly
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext
from fastmcp.client.logging import LogMessage

# Simple mock LLM sampling handler
async def mock_sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    context: RequestContext
) -> str:
    """Mock LLM that returns a simple summary."""
    return "This is a mock summary of the provided content."

# Log handler to capture server logs
async def log_handler(log_message: LogMessage):
    """Handle log messages from the server."""
    level = log_message.level.upper()
    logger = log_message.logger or "server"
    message = log_message.data
    print(f"[{level}] {logger}: {message}")

async def main():
    """Main client function using in-memory server."""
    print("Creating in-memory client connection...")
    
    try:
        # Connect directly to the server instance with logging
        client = Client(
            mcp, 
            sampling_handler=mock_sampling_handler,
            log_handler=log_handler
        )
        
        async with client:
            print("Connected to server!")
            
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            print("\n" + "="*50)
            print("Testing greet tool...")
            print("="*50)
            result = await client.call_tool("greet", {"name": "World"})
            print(f"Greet result: {result[0].text}")
            
            print("\n" + "="*50)
            print("Testing summary tool...")
            print("="*50)
            result = await client.call_tool("generate_summary", {
                "content": "This is a long piece of text that needs to be summarized for testing purposes."
            })
            print(f"Summary result: {result[0].text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
