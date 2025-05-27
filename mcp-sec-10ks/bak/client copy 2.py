#!/usr/bin/env python3
"""
Command Line MCP Client with Sampling Support using OpenRouter
"""
import asyncio
import argparse
import os
import sys
from typing import Optional
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MCPFinancialClient:
    def __init__(self, model_name: str, server_script: str = "./main.py"):
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
    
    async def handle_sampling_request(
        self, 
        ctx,  # MCP context parameter
        message: types.CreateMessageRequestParams
    ) -> types.CreateMessageResult:
        """
        Handle sampling requests from the MCP server
        """
        try:
            print(f"🤖 Sampling request received for model: {self.model_name}")
            print(f"📝 Processing prompt with {len(message.messages)} messages...")
            
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
            
            print(f"🔍 Making API call to OpenRouter with {len(openai_messages)} messages...")
            
            # Make the API call to OpenRouter
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                max_tokens=getattr(message, 'maxTokens', 4000),
                temperature=0.1  # Low temperature for consistent financial data extraction
            )
            
            # Extract the response
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            print(f"✅ Sampling completed. Finish reason: {finish_reason}")
            print(f"📊 Response length: {len(content) if content else 0} characters")
            
            # Convert finish reason to MCP stop reason
            stop_reason_mapping = {
                "stop": "endTurn",
                "length": "maxTokens",
                "content_filter": "contentFilter",
                "function_call": "toolUse"
            }
            stop_reason = stop_reason_mapping.get(finish_reason, "endTurn")
            
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
            print(f"📋 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"Error processing request: {str(e)}"
                ),
                model=self.model_name,
                stopReason="error"
            )
    
    async def process_company(self, company_name: str, year: int, cik: str):
        """
        Process a single company's financial data
        """
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        print(f"🏢 Processing {company_name} (CIK: {cik}) for year {year}")
        print(f"🔗 Connecting to MCP server: {self.server_script}")
        
        try:
            # Connect to the MCP server
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(
                    read, 
                    write, 
                    sampling_callback=self.handle_sampling_request
                ) as session:
                    # Initialize the connection
                    await session.initialize()
                    print("✅ Connected to MCP server")
                    
                    # List available tools (for debugging)
                    try:
                        tools = await session.list_tools()
                        print(f"📋 Available tools: {tools}")
                        # Handle different tool response formats
                        if hasattr(tools, 'tools'):
                            tool_names = [tool.name for tool in tools.tools]
                        elif isinstance(tools, list):
                            tool_names = [getattr(tool, 'name', str(tool)) for tool in tools]
                        else:
                            tool_names = [str(tools)]
                        print(f"📋 Tool names: {tool_names}")
                    except Exception as list_error:
                        print(f"❌ Error listing tools: {list_error}")
                        print(f"📋 List error type: {type(list_error).__name__}")
                        # Don't raise here, continue anyway
                        pass
                    
                    # Call the financial data processing tool
                    print(f"🔄 Calling process_financial_data tool...")
                    try:
                        result = await session.call_tool(
                            "process_financial_data",
                            arguments={
                                "company_name": company_name,
                                "year": year,
                                "cik": cik
                            }
                        )
                    except Exception as tool_error:
                        print(f"❌ Tool call error: {tool_error}")
                        print(f"📋 Tool error type: {type(tool_error).__name__}")
                        import traceback
                        print(f"📋 Tool traceback: {traceback.format_exc()}")
                        raise
                    
                    print("🎯 Financial data processing completed!")
                    print("=" * 80)
                    print("📊 RESULT:")
                    print("=" * 80)
                    
                    # Handle different result types
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
                    
        except Exception as e:
            print(f"❌ Error processing company: {e}")
            print(f"📋 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Full traceback:")
            traceback.print_exc()
            raise


def main():
    parser = argparse.ArgumentParser(
        description="MCP Client for Financial Data Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model anthropic/claude-3.5-sonnet --company "Apple Inc" --year 2023 --cik 320193
  %(prog)s --model openai/gpt-4o --company "Microsoft" --year 2023 --cik 789019
  %(prog)s --model meta-llama/llama-3.1-8b-instruct --company "Tesla" --year 2023 --cik 1318605

Environment Variables:
  OPENROUTER_API_KEY: Your OpenRouter API key (required)
        """
    )
    
    parser.add_argument(
        "--model", 
        required=True,
        help="Model name for OpenRouter (e.g., 'anthropic/claude-3.5-sonnet', 'openai/gpt-4o')"
    )
    parser.add_argument(
        "--company", 
        required=True,
        help="Company name"
    )
    parser.add_argument(
        "--year", 
        type=int, 
        required=True,
        help="Year for the financial data"
    )
    parser.add_argument(
        "--cik", 
        required=True,
        help="Company CIK (Central Index Key)"
    )
    parser.add_argument(
        "--server-script",
        default="./main.py",
        help="Path to the MCP server script (default: ./main.py)"
    )
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable is required")
        print("Please set it with: export OPENROUTER_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Validate server script exists
    if not os.path.exists(args.server_script):
        print(f"❌ Error: Server script not found: {args.server_script}")
        sys.exit(1)
    
    print("🚀 MCP Financial Data Extraction Client")
    print(f"🤖 Model: {args.model}")
    print(f"🏢 Company: {args.company}")
    print(f"📅 Year: {args.year}")
    print(f"🔢 CIK: {args.cik}")
    print(f"🖥️  Server: {args.server_script}")
    print("-" * 80)
    
    try:
        # Create and run the client
        client = MCPFinancialClient(args.model, args.server_script)
        asyncio.run(client.process_company(args.company, args.year, args.cik))
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()