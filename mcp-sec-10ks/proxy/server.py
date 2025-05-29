import asyncio
import logging
import sys
from fastmcp import FastMCP, Client
from proxy import proxy

# Configure logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create the main MCP server
mcp = FastMCP(name="GreetingServer")

# Create proxy client using the imported proxy server
proxy_client = Client(proxy)

@mcp.tool()
async def greet(name: str) -> str:
    """Greet someone by name with an enhanced friendly message."""
    logger.info(f"Greeting request for: {name}")
    
    try:
        # Create basic greeting
        basic_greeting = f"Hello, {name}! Welcome to FastMCP!"
        
        # Use proxy client to enhance the greeting with LLM
        async with proxy_client:
            result = await proxy_client.call_tool("enhance_greeting_with_llm", {"basic_greeting": basic_greeting})
            enhanced_greeting = result[0].text
        
        logger.info("Greeting successfully enhanced")
        return enhanced_greeting
        
    except Exception as e:
        logger.error(f"Error in greet: {e}")
        return f"Hello, {name}! (Enhanced greeting unavailable)"

if __name__ == "__main__":
    logger.info("Starting GreetingServer")
    mcp.run()
