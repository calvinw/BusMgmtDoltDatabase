import os
import logging
import sys
from fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Create the proxy MCP server
proxy = FastMCP(name="LLMProxy")

# Initialize OpenAI client with OpenRouter configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@proxy.tool()
async def call_llm(
    prompt: str,
    model: str = "anthropic/claude-3.5-sonnet",
    max_tokens: int = 4000,
    temperature: float = 0.1
) -> str:
    """Call an LLM via OpenRouter API with the provided prompt."""
    logger.info(f"Calling LLM with model: {model}")
    
    try:
        # Check if API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.warning("OPENROUTER_API_KEY not found")
            return f"Error: OPENROUTER_API_KEY not found in environment variables."
        
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract the response
        result = response.choices[0].message.content.strip()
        logger.info("LLM call completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return f"Error calling LLM: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting LLMProxy")
    proxy.run()
