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
proxy = FastMCP(name="GreetingEnhancerProxy")

# Initialize OpenAI client with OpenRouter configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@proxy.tool()
async def enhance_greeting_with_llm(basic_greeting: str, model: str = "anthropic/claude-3.5-sonnet") -> str:
    """Enhance a basic greeting using an LLM via OpenRouter API."""
    logger.info(f"Enhancing greeting with model: {model}")
    
    try:
        # Check if API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.warning("OPENROUTER_API_KEY not found")
            return f"Error: OPENROUTER_API_KEY not found in environment variables. Original greeting: {basic_greeting}"
        
        # Create the prompt for the LLM
        prompt = f"""Please enhance this basic greeting to make it more creative, warm, and engaging while keeping it professional and friendly. Add some personality but don't make it too long.

Basic greeting: {basic_greeting}

Enhanced greeting:"""

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        # Extract the enhanced greeting from the response
        enhanced_greeting = response.choices[0].message.content.strip()
        logger.info("Greeting enhanced successfully")
        
        return enhanced_greeting
        
    except Exception as e:
        logger.error(f"Error enhancing greeting with LLM: {e}")
        return f"Error enhancing greeting with LLM: {str(e)}. Original greeting: {basic_greeting}"

if __name__ == "__main__":
    logger.info("Starting GreetingEnhancerProxy")
    proxy.run()
