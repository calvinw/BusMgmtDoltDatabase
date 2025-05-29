# debug_client.py
"""
Debug client using in-memory transport (recommended approach)
"""

import asyncio
import sys
import traceback

async def test_in_memory_connection():
    """Test in-memory connection with detailed error reporting"""
    
    try:
        print("Testing in-memory connection (recommended approach)...")
        
        # Import the main server directly
        from main_mcp_server import mcp
        from fastmcp import Client
        
        print("✅ Successfully imported main server and FastMCP Client")
        
        # Use in-memory transport
        async with Client(mcp) as client:
            print("✅ Connected successfully using in-memory transport!")
            
            # List tools
            print("Listing available tools...")
            tools = await client.list_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Test the greet tool
            print("Testing greet tool with 'TestUser'...")
            result = await client.call_tool("greet", {"name": "TestUser"})
            print(f"✅ Tool call successful!")
            
            # Handle different result formats
            if hasattr(result, 'text'):
                print(f"Result: {result.text}")
            elif hasattr(result, 'content') and result.content:
                # Handle list of content items
                if isinstance(result.content, list) and len(result.content) > 0:
                    # Extract text from TextContent object
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        print(f"Result: {content_item.text}")
                    else:
                        print(f"Result: {content_item}")
                else:
                    print(f"Result: {result.content}")
            else:
                print(f"Result: {result}")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure main_mcp_server.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Exception type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

async def main():
    print("=== FastMCP In-Memory Connection Debug ===")
    print()
    
    # Test if we can import FastMCP
    try:
        from fastmcp import FastMCP, Client
        print("✅ FastMCP imports successful")
    except ImportError as e:
        print(f"❌ FastMCP import failed: {e}")
        print("Run: pip install fastmcp")
        return
    
    # Test the in-memory connection
    success = await test_in_memory_connection()
    
    if success:
        print("\n🎉 Everything working! You can now use simple_client.py")
    else:
        print("\n🔍 Debug suggestions:")
        print("1. Make sure main_mcp_server.py exists in current directory")
        print("2. Check that OPENROUTER_API_KEY is set: echo $OPENROUTER_API_KEY")
        print("3. Verify all files are present: ls -la *.py")
        print("4. Try reinstalling: pip install --upgrade fastmcp openai")

if __name__ == "__main__":
    asyncio.run(main())
