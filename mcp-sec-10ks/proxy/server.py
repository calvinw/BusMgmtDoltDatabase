import asyncio
from fastmcp import FastMCP, Client
from proxy import proxy

# Create the main MCP server
mcp = FastMCP(name="GreetingServer")

# Create proxy client using the imported proxy server
proxy_client = Client(proxy)

@mcp.tool()
async def greet(name: str) -> str:
    """Greet someone by name with an enhanced friendly message."""
    # Create basic greeting
    basic_greeting = f"Hello, {name}! Welcome to FastMCP!"
    
    # Use proxy client to enhance the greeting with LLM
    async with proxy_client:
        result = await proxy_client.call_tool("enhance_greeting_with_llm", {"basic_greeting": basic_greeting})
        enhanced_greeting = result[0].text
    
    return enhanced_greeting

if __name__ == "__main__":
    mcp.run()
