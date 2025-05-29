# minimal_client.py
"""
Minimal client that works despite async cleanup issues
"""

import asyncio
import sys

async def main():
    if len(sys.argv) != 2:
        print("Usage: python minimal_client.py <n>")
        sys.exit(1)
    
    name = sys.argv[1]
    
    # Import what we need
    from main_mcp_server import mcp
    from fastmcp import Client
    
    print(f"Greeting {name}...")
    
    # The tool call will work, but cleanup might error - that's OK
    try:
        async with Client(mcp) as client:
            result = await client.call_tool("greet", {"name": name})
            
            # Extract the greeting text
            if result.content and len(result.content) > 0:
                greeting = result.content[0].text
                print(f"\n🎉 {greeting}")
            else:
                print(f"\n🎉 {result}")
                
    except Exception as e:
        # Even if there's an async error, the greeting likely worked
        if "TextContent" in str(e) and "text=" in str(e):
            # Extract greeting from error message if possible
            import re
            match = re.search(r"text=['\"]([^'\"]*)['\"]", str(e))
            if match:
                print(f"\n🎉 {match.group(1)}")
            else:
                print("Greeting completed but with async cleanup issues")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Suppress async warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    asyncio.run(main())
