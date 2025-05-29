from fastmcp import FastMCP

# Create the proxy MCP server
proxy = FastMCP(name="GreetingEnhancerProxy")

@proxy.tool()
def enhance_greeting(basic_greeting: str) -> str:
    """Enhance a basic greeting with additional friendly text and emojis."""
    enhanced = f"🎉 {basic_greeting} 🎉\n"
    enhanced += "Hope you're having a wonderful day! ✨\n"
    enhanced += "Thanks for using our FastMCP greeting service! 🚀"
    return enhanced

if __name__ == "__main__":
    proxy.run()
