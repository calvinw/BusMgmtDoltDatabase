# llm_proxy_server.py
"""
Simple LLM Proxy MCP Server using OpenRouter API
Provides one tool: call_llm for LLM completions
"""

from fastmcp import FastMCP
from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("llm-proxy")

# Configuration - Using OpenRouter instead of OpenAI directly
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key-here")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"  # Good balance of speed/cost on OpenRouter

# Create OpenAI-compatible client for OpenRouter
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
)

@mcp.tool()
async def call_llm(prompt: str) -> str:
    """Call LLM via OpenRouter with a prompt and return the response"""
    logger.info(f"LLM tool called with prompt: {prompt[:50]}...")
    
    try:
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        logger.info(f"LLM response received: {result[:50]}...")
        return result
                
    except Exception as e:
        logger.error(f"Exception calling LLM via OpenRouter: {e}")
        return f"Error calling LLM: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting LLM Proxy MCP Server (OpenRouter)")
    logger.info(f"Using model: {DEFAULT_MODEL}")
    logger.info("Available tools: call_llm")
    mcp.run()
