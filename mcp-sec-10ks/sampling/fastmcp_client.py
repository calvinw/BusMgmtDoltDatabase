#!/usr/bin/env python3
"""
Simple FastMCP Client with OpenRouter Integration
"""
import asyncio
import argparse
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleFastMCPClient:
    def __init__(self, model_name: str, server_script: str = "./fastmcp_server.py"):
        self.model_name = model_name
        self.server_script = server_script
        self.openai_client = None
        self._setup_openai_client()
    
    def _setup_openai_client(self):
        """Setup OpenAI client with OpenRouter configuration"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.openai_client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    
    async def handle_logging(self, params):
        """Handle logging messages from the server"""
        from mcp import types
        
        # Extract log level and message from the logging notification
        level = getattr(params, 'level', 'info').upper()
        data = getattr(params, 'data', str(params))
        
        # Print with nice formatting
        print(f"[SERVER {level}] {data}")
    
    async def handle_sampling_request(self, ctx, message):
        """Handle sampling requests from the MCP server"""
        try:
            print(f"🤖 Sampling request received for model: {self.model_name}")
            
            # Convert MCP messages to OpenAI format
            openai_messages = []
            
            # Add system prompt if provided
            if hasattr(message, 'systemPrompt') and message.systemPrompt:
                openai_messages.append({
                    "role": "system",
                    "content": message.systemPrompt
                })
            
            # Convert MCP messages
            for msg in message.messages:
                if msg.role in ["user", "assistant", "system"]:
                    if hasattr(msg.content, 'text'):
                        content = msg.content.text
                    elif isinstance(msg.content, str):
                        content = msg.content
                    else:
                        content = str(msg.content)
                    
                    openai_messages.append({
                        "role": msg.role,
                        "content": content
                    })
            
            # Make the API call to OpenRouter
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=getattr(message, 'maxTokens', 1000),
                temperature=getattr(message, 'temperature', 0.7)
            )
            
            # Extract the response
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            print(f"✅ Sampling completed. Finish reason: {finish_reason}")
            
            # Convert finish reason to MCP stop reason
            stop_reason_mapping = {
                "stop": "endTurn",
                "length": "maxTokens",
                "content_filter": "contentFilter",
                "function_call": "toolUse"
            }
            stop_reason = stop_reason_mapping.get(finish_reason, "endTurn")
            
            # Import the types we need
            from mcp import types
            
            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=content or ""
                ),
                model=self.model_name,
                stopReason=stop_reason
            )
            
        except Exception as e:
            print(f"❌ Error in sampling: {e}")
            from mcp import types
            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"Error processing request: {str(e)}"
                ),
                model=self.model_name,
                stopReason="error"
            )
    
    async def test_sampling(self, question: str):
        """Test the sampling functionality"""
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        print(f"🚀 Testing FastMCP sampling with question: '{question}'")
        print(f"🔗 Connecting to server: {self.server_script}")
        
        # Create a log handler to capture server log messages
        def log_handler(message):
            """Handle log messages from the server"""
            level = getattr(message, 'level', 'info').upper()
            data = getattr(message, 'data', str(message))
            print(f"[SERVER {level}] {data}")
        
        try:
            # Connect to the MCP server
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(
                    read, 
                    write, 
                    sampling_callback=self.handle_sampling_request,
                    logging_callback=self.handle_logging
                ) as session:
                    # Initialize the connection
                    await session.initialize()
                    print("✅ Connected to FastMCP server")
                    
                    # List available tools
                    tools = await session.list_tools()
                    print(f"📋 Available tools: {[tool.name for tool in tools.tools]}")
                    
                    # Call the ask_question tool
                    print(f"🔄 Calling ask_question tool...")
                    print("📝 Server logs will appear below:")
                    print("-" * 60)
                    
                    result = await session.call_tool(
                        "ask_question",
                        arguments={"question": question}
                    )
                    
                    print("-" * 60)
                    print("🎯 Question answered!")
                    print("=" * 80)
                    print("📊 RESULT:")
                    print("=" * 80)
                    
                    # Handle the result
                    if hasattr(result, 'content'):
                        if isinstance(result.content, list):
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    print(content_item.text)
                                else:
                                    print(str(content_item))
                        else:
                            print(result.content)
                    else:
                        print(str(result))
                    
                    print("=" * 80)
                    
                    # Test the logging tool as well
                    print("\n🧪 Testing logging functionality...")
                    print("📝 Server logs for logging test:")
                    print("-" * 60)
                    
                    log_result = await session.call_tool(
                        "test_logging",
                        arguments={"message": "debug warning success test"}
                    )
                    
                    print("-" * 60)
                    print("🧪 Logging test result:")
                    if hasattr(log_result, 'content'):
                        if isinstance(log_result.content, list):
                            for content_item in log_result.content:
                                if hasattr(content_item, 'text'):
                                    print(content_item.text)
                                else:
                                    print(str(content_item))
                        else:
                            print(log_result.content)
                    else:
                        print(str(log_result))
                    
        except Exception as e:
            print(f"❌ Error testing sampling: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    parser = argparse.ArgumentParser(
        description="Simple FastMCP Client for Testing Sampling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model anthropic/claude-3.5-sonnet --question "What is the capital of France?"
  %(prog)s --model openai/gpt-4o --question "Explain quantum computing in simple terms"

Environment Variables:
  OPENROUTER_API_KEY: Your OpenRouter API key (required)
        """
    )
    
    parser.add_argument(
        "--model", 
        required=True,
        help="Model name for OpenRouter (e.g., 'anthropic/claude-3.5-sonnet')"
    )
    parser.add_argument(
        "--question", 
        required=True,
        help="Question to ask the LLM"
    )
    parser.add_argument(
        "--server-script",
        default="./fastmcp_server.py",
        help="Path to the FastMCP server script (default: ./fastmcp_server.py)"
    )
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable is required")
        sys.exit(1)
    
    # Validate server script exists
    if not os.path.exists(args.server_script):
        print(f"❌ Error: Server script not found: {args.server_script}")
        sys.exit(1)
    
    print("🚀 Simple FastMCP Sampling Test")
    print(f"🤖 Model: {args.model}")
    print(f"❓ Question: {args.question}")
    print(f"🖥️  Server: {args.server_script}")
    print("-" * 80)
    
    try:
        # Create and run the client
        client = SimpleFastMCPClient(args.model, args.server_script)
        asyncio.run(client.test_sampling(args.question))
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
