#!/usr/bin/env python3
"""
Enhanced MCP Client with CSV Batch Processing Support
"""
import asyncio
import argparse
import os
import sys
import csv
from typing import Optional, List, Dict
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MCPFinancialBatchClient:
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
        """Handle sampling requests from the MCP server"""
        try:
            # Extract company info from the prompt for better logging
            company_info = self._extract_company_info_from_prompt(message)
            if company_info:
                print(f"🤖 Sampling request for {company_info['company']} ({company_info['year']}) using model: {self.model_name}")
            else:
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
                temperature=0.1
            )
            
            # Extract the response
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Enhanced completion logging
            if company_info:
                print(f"✅ Completed sampling for {company_info['company']} ({company_info['year']}) - Finish reason: {finish_reason}")
            else:
                print(f"✅ Sampling completed - Finish reason: {finish_reason}")
            
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
            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text=f"Error processing request: {str(e)}"
                ),
                model=self.model_name,
                stopReason="error"
            )
    
    def _extract_company_info_from_prompt(self, message: types.CreateMessageRequestParams) -> Optional[Dict[str, str]]:
        """Extract company name and year from the sampling prompt"""
        try:
            # Look through all messages for company info
            for msg in message.messages:
                content = ""
                if hasattr(msg.content, 'text'):
                    content = msg.content.text
                elif isinstance(msg.content, str):
                    content = msg.content
                else:
                    content = str(msg.content)
                
                # Look for company name pattern in the prompt
                import re
                
                # Pattern 1: Look for company name in quotes
                company_match = re.search(r'Company name: "([^"]+)"', content)
                if not company_match:
                    # Pattern 2: Look for company name after "The company name should be"  
                    company_match = re.search(r'company name should be "([^"]+)"', content)
                
                # Pattern 3: Look for year information
                year_match = re.search(r'(\d{4})', content)
                
                if company_match:
                    company_name = company_match.group(1)
                    year = year_match.group(1) if year_match else "Unknown"
                    
                    return {
                        "company": company_name,
                        "year": year
                    }
            
            return None
            
        except Exception:
            # If extraction fails, just return None - not critical
            return None
    
    async def process_batch(self, companies: List[Dict[str, any]]):
        """Process a batch of companies and return consolidated results"""
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        print(f"🏢 Processing batch of {len(companies)} companies")
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
                    
                    # Process batch of companies
                    print(f"🔄 Calling process_financial_batch tool...")
                    result = await session.call_tool(
                        "process_financial_batch",
                        arguments={
                            "companies": companies
                        }
                    )
                    
                    print("🎯 Batch financial data processing completed!")
                    print("=" * 80)
                    print("📊 BULK INSERT STATEMENT:")
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
            print(f"❌ Error processing batch: {e}")
            import traceback
            traceback.print_exc()
            raise

def load_companies_from_csv(file_path: str) -> List[Dict[str, any]]:
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
        description="MCP Batch Client for Financial Data Extraction (CSV Input)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model anthropic/claude-3.5-sonnet --csv companies.csv
  %(prog)s --model openai/gpt-4o --csv my_portfolio.csv

CSV Format (headers can be named flexibly):
company_name,year,cik
Apple Inc,2023,320193
Microsoft Corporation,2023,789019
Tesla Inc,2023,1318605

Supported header names (case insensitive):
- Company: company_name, company, name, "company name"
- Year: year, fiscal_year, fy  
- CIK: cik, cik_number, central_index_key

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
        "--csv", 
        required=True,
        help="CSV file containing list of companies to process"
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
        sys.exit(1)
    
    # Validate server script exists
    if not os.path.exists(args.server_script):
        print(f"❌ Error: Server script not found: {args.server_script}")
        sys.exit(1)
    
    # Load companies list
    companies = load_companies_from_csv(args.csv)
    
    if not companies:
        print("❌ Error: No valid companies found in CSV file")
        sys.exit(1)
    
    print("🚀 MCP Batch Financial Data Extraction Client (CSV)")
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
        client = MCPFinancialBatchClient(args.model, args.server_script)
        asyncio.run(client.process_batch(companies))
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()