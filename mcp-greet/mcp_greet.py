#!/usr/bin/env python3
"""
Simple MCP Server using FastMCP
"""
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("My MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Nice to meet you."

@mcp.tool()
def greet_in_german(name: str) -> str:
    """Greet in German."""
    return f"Guten Tag, {name}! Wie geht's."


@mcp.tool()
def get_sample_markdown_table() -> str:
    """Markdown table."""
    return f"""
    | Header 1 | Header 2 |
    |----------|----------|
    | Cell 1   | Cell 2   |
    | Cell 3   | Cell 4   |
    """

if __name__ == "__main__":
    mcp.run()
