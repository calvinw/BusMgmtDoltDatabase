# main_mcp_server.py
"""
Main MCP Server with greet tool that uses LLM proxy behind the scenes
"""

from fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import logging
import os
from contextlib import AsyncExitStack
from typing import Optional
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("main-server")

# Global variables for LLM proxy connection
llm_session: Optional[ClientSession] = None
llm_exit_stack: Optional[AsyncExitStack] = None

async def connect_to_llm_proxy():
    """Connect to the LLM proxy MCP server"""
    global llm_session, llm_exit_stack
    
    try:
        logger.info("Connecting to LLM proxy MCP server...")
        
        # Check if LLM proxy file exists
        proxy_file = Path("llm_proxy_server.py")
        if not proxy_file.exists():
            logger.error(f"LLM proxy file not found: {proxy_file}")
            return False
        
        # Create server parameters for the LLM proxy
        server_params = StdioServerParameters(
            command="python",
            args=[str(proxy_file.absolute())]
        )
        
        # Create exit stack for proper cleanup
        llm_exit_stack = AsyncExitStack()
        
        # Connect to the LLM proxy
        stdio_transport = await llm_exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        
        # Create client session
        llm_session = await llm_exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        # Initialize the session
        await llm_session.initialize()
        
        logger.info("✅ Connected to LLM proxy successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to LLM proxy: {e}")
        llm_session = None
        if llm_exit_stack:
            try:
                await llm_exit_stack.aclose()
            except:
                pass
            llm_exit_stack = None
        return False

async def call_llm_tool(prompt: str) -> str:
    """Call the call_llm tool on the LLM proxy server"""
    global llm_session
    
    if not llm_session:
        # Try to connect
        logger.info("LLM session not available, attempting to connect...")
        if not await connect_to_llm_proxy():
            return "Error: Could not connect to LLM proxy"
    
    try:
        logger.info("Calling LLM proxy tool...")
        result = await llm_session.call_tool("call_llm", {"prompt": prompt})
        logger.info("LLM proxy call successful")
        return result.content[0].text
        
    except Exception as e:
        logger.error(f"Error calling LLM tool: {e}")
        # Reset connection for next attempt
        llm_session = None
        return f"Error calling LLM: {e}"

@mcp.tool()
async def greet(name: str) -> str:
    """
    Greet someone with an AI-enhanced personalized greeting
    
    Args:
        name: The person's name to greet
    
    Returns:
        An AI-enhanced personalized greeting
    """
    logger.info(f"Greet tool called for: {name}")
    
    # Create a prompt for the LLM
    prompt = f"Create a warm, friendly, and personalized greeting for someone named {name}. Make it creative and memorable."
    
    # Call the LLM proxy (client knows nothing about this!)
    logger.info("Calling LLM proxy for greeting enhancement...")
    enhanced_greeting = await call_llm_tool(prompt)
    
    # Return the result
    if not enhanced_greeting.startswith("Error:"):
        logger.info(f"Successfully created greeting for {name}")
        return enhanced_greeting
    else:
        # Fallback to basic greeting if LLM fails
        logger.warning(f"LLM failed, using fallback: {enhanced_greeting}")
        return f"Hello, {name}! Nice to meet you. (AI enhancement unavailable: {enhanced_greeting})"

if __name__ == "__main__":
    logger.info("=== Main MCP Server Starting ===")
    
    logger.info("Starting Main MCP Server...")
    
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
