"""
Simple FastMCP Server with Logging
"""
from fastmcp import FastMCP, Context

# Create the FastMCP server
mcp = FastMCP(name="SimpleServer")

@mcp.tool()
async def greet(name: str, ctx: Context) -> str:
    """Greet someone by name."""
    await ctx.info(f"Greeting request received for name: {name}")
    await ctx.debug(f"Processing greeting with name length: {len(name)}")
    
    result = f"Hello, {name}!"
    
    await ctx.info(f"Greeting completed successfully")
    return result

@mcp.tool()
async def generate_summary(content: str, ctx: Context) -> str:
    """Generate a summary using LLM sampling."""
    await ctx.info(f"Summary request received for {len(content)} character content")
    await ctx.debug(f"Content preview: {content[:50]}...")
    
    try:
        await ctx.info("Requesting LLM sampling for summary generation")
        # Use the client's LLM to generate a summary
        summary = await ctx.sample(f"Please summarize this text: {content}")
        
        await ctx.info(f"LLM sampling completed, summary length: {len(summary.text)}")
        await ctx.debug(f"Summary preview: {summary.text[:30]}...")
        
        return summary.text
        
    except Exception as e:
        await ctx.error(f"Error during summary generation: {str(e)}")
        await ctx.warning("Falling back to simple summary")
        return f"Summary unavailable. Original content was {len(content)} characters long."

# Main execution block - only used if running server standalone
if __name__ == "__main__":
    print("Starting FastMCP server...")
    try:
        mcp.run()
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
