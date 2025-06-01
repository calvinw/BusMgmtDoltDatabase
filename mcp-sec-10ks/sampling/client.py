#!/usr/bin/env python3
"""
Simplified MCP Client with FastMCP approach and OpenRouter Integration
"""
import asyncio
import argparse
import os
import sys
import csv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimplifiedFinancialClient:
    def __init__(self, model_name: str, server_script: str = "./mcp_sec_10ks.py"):
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
                max_tokens=getattr(message, 'maxTokens', 4000),
                temperature=0.1  # Low temperature for consistent financial data extraction
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
    
    async def process_company(self, company_name: str, year: int, cik: str):
        """Process a single company's financial data"""
        companies = [{"company_name": company_name, "year": year, "cik": cik}]
        await self.process_companies(companies)
    
    async def process_companies(self, companies: list):
        """Process multiple companies and generate bulk INSERT statement"""
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        print(f"🏢 Processing {len(companies)} companies")
        print(f"🔗 Connecting to MCP server: {self.server_script}")
        
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
                    print("✅ Connected to MCP server")
                    
                    # List available tools
                    tools = await session.list_tools()
                    print(f"📋 Available tools: {[tool.name for tool in tools.tools]}")
                    
                    # Call the appropriate tool based on number of companies
                    if len(companies) == 1:
                        # Single company - use original tool
                        company = companies[0]
                        print(f"🔄 Calling process_financial_data tool...")
                        print("📝 Server logs will appear below:")
                        print("-" * 60)
                        
                        result = await session.call_tool(
                            "process_financial_data",
                            arguments={
                                "company_name": company["company_name"],
                                "year": company["year"],
                                "cik": company["cik"]
                            }
                        )
                        
                        print("-" * 60)
                        print("🎯 Financial data processing completed!")
                        print("=" * 80)
                        print("📊 RESULT:")
                        print("=" * 80)
                    else:
                        # Multiple companies - use batch tool
                        print(f"🔄 Calling process_financial_batch tool...")
                        print("📝 Server logs will appear below:")
                        print("-" * 60)
                        
                        result = await session.call_tool(
                            "process_financial_batch",
                            arguments={"companies": companies}
                        )
                        
                        print("-" * 60)
                        print("🎯 Batch processing completed!")
                        print("=" * 80)
                        print("📊 BULK INSERT STATEMENT:")
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
                    
        except Exception as e:
            print(f"❌ Error processing companies: {e}")
            import traceback
            traceback.print_exc()
            raise

def load_companies_from_csv(file_path: str) -> list:
    """Load companies from CSV file"""
    try:
        companies = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Print detected headers for debugging
            print(f"📋 Detected CSV headers: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
                try:
                    # Handle different possible column names (case insensitive)
                    company_name = None
                    year = None
                    cik = None
                    
                    # Find company name column
                    for key in row.keys():
                        if key and key.lower().strip() in ['company_name', 'company', 'name', 'company name']:
                            company_name = row[key].strip()
                            break
                    
                    # Find year column  
                    for key in row.keys():
                        if key and key.lower().strip() in ['year', 'fiscal_year', 'fy']:
                            year = int(row[key].strip()) if row[key].strip() else None
                            break
                    
                    # Find CIK column
                    for key in row.keys():
                        if key and key.lower().strip() in ['cik', 'cik_number', 'central_index_key']:
                            cik = row[key].strip()
                            break
                    
                    # Validate required fields
                    if not company_name:
                        print(f"⚠️  Warning: Missing company name in row {row_num}, skipping")
                        continue
                    if not year:
                        print(f"⚠️  Warning: Missing or invalid year in row {row_num}, skipping")
                        continue
                    if not cik:
                        print(f"⚠️  Warning: Missing CIK in row {row_num}, skipping")
                        continue
                    
                    companies.append({
                        "company_name": company_name,
                        "year": year,
                        "cik": cik
                    })
                    
                except ValueError as e:
                    print(f"⚠️  Warning: Invalid data in row {row_num}: {e}, skipping")
                    continue
                except Exception as e:
                    print(f"⚠️  Warning: Error processing row {row_num}: {e}, skipping")
                    continue
        
        print(f"📊 Loaded {len(companies)} valid companies from CSV")
        return companies
        
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Simplified MCP Client for Financial Data Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single company:
    %(prog)s --model anthropic/claude-3.5-sonnet --company "Apple Inc" --year 2023 --cik 320193
  
  Batch processing from CSV:
    %(prog)s --model google/gemini-2.5-flash-preview-05-20 --csv companies.csv

CSV Format (headers can be named flexibly):
company_name,year,cik
Apple Inc,2023,320193
Microsoft Corporation,2023,789019

Environment Variables:
  OPENROUTER_API_KEY: Your OpenRouter API key (required)
        """
    )
    
    parser.add_argument(
        "--model", 
        required=True,
        help="Model name for OpenRouter (e.g., 'anthropic/claude-3.5-sonnet', 'openai/gpt-4o')"
    )
    
    # Single company arguments
    parser.add_argument(
        "--company", 
        help="Company name (for single company processing)"
    )
    parser.add_argument(
        "--year", 
        type=int, 
        help="Year for the financial data (for single company processing)"
    )
    parser.add_argument(
        "--cik", 
        help="Company CIK (for single company processing)"
    )
    
    # Batch processing argument
    parser.add_argument(
        "--csv", 
        help="CSV file containing list of companies to process (for batch processing)"
    )
    
    parser.add_argument(
        "--server-script",
        default="./mcp_sec_10ks.py",
        help="Path to the MCP server script (default: ./mcp_sec_10ks.py)"
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
    
    # Determine processing mode
    if args.csv:
        # Batch processing mode
        companies = load_companies_from_csv(args.csv)
        
        if not companies:
            print("❌ Error: No valid companies found in CSV file")
            sys.exit(1)
        
        print("🚀 Simplified MCP Financial Data Extraction Client (Batch Mode)")
        print(f"🤖 Model: {args.model}")  
        print(f"📁 CSV File: {args.csv}")
        print(f"📊 Total Companies: {len(companies)}")
        print(f"🖥️  Server: {args.server_script}")
        print("-" * 80)
        
        # Show preview of companies to be processed
        print("📋 Companies to process:")
        for i, company in enumerate(companies[:5]):  # Show first 5
            print(f"   {i+1}. {company['company_name']} ({company['year']}) - CIK: {company['cik']}")
        if len(companies) > 5:
            print(f"   ... and {len(companies) - 5} more")
        print("-" * 80)
        
        try:
            # Create and run the batch client
            client = SimplifiedFinancialClient(args.model, args.server_script)
            asyncio.run(client.process_companies(companies))
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)
        
    elif args.company and args.year and args.cik:
        # Single company mode
        print("🚀 Simplified MCP Financial Data Extraction Client (Single Company)")
        print(f"🤖 Model: {args.model}")
        print(f"🏢 Company: {args.company}")
        print(f"📅 Year: {args.year}")
        print(f"🔢 CIK: {args.cik}")
        print(f"🖥️  Server: {args.server_script}")
        print("-" * 80)
        
        try:
            # Create and run the single company client
            client = SimplifiedFinancialClient(args.model, args.server_script)
            asyncio.run(client.process_company(args.company, args.year, args.cik))
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)
        
    else:
        print("❌ Error: Must specify either:")
        print("  Single company: --company, --year, and --cik")
        print("  Batch processing: --csv")
        sys.exit(1)

if __name__ == "__main__":
    main()
