# simple_client.py
"""
Simple FastMCP client that greets one person via command line argument
"""

from fastmcp import Client
import asyncio
import sys

async def main():
    """Main client function"""
    # Get name from command line
    if len(sys.argv) != 2:
        print("Usage: python simple_client.py <name>")
        print("Example: python simple_client.py Alice")
        sys.exit(1)
    
    name = sys.argv[1]
    
    try:
        # Connect to main MCP server and call greet tool
        async with Client("main_mcp_server.py") as client:
            result = await client.call_tool("greet", {"name": name})
            print(result.text)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
