import asyncio
import sys
from fastmcp import Client
from server import mcp

async def main():
    # Check if name was provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python client.py <name>")
        print("Example: python client.py Alice")
        sys.exit(1)
    
    name_to_greet = sys.argv[1]
    
    # Create client with in-memory transport using imported server
    client = Client(mcp)
    
    try:
        # Use async context manager for the client
        async with client:
            print(f"Calling greet tool with name: {name_to_greet}")
            
            # Call the greet tool
            result = await client.call_tool("greet", {"name": name_to_greet})
            
            # Display the result
            print(f"Server response: {result[0].text}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
