#!/usr/bin/env python3
"""
Financial Data Extraction Client using proxy architecture
"""
import asyncio
import argparse
import os
import sys
import csv
from fastmcp import Client
from server import mcp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def process_company(company_name: str, year: int, cik: str, model: str):
    """Process a single company's financial data"""
    companies = [{"company_name": company_name, "year": year, "cik": cik}]
    await process_companies(companies, model)

async def process_companies(companies: list, model: str):
    """Process multiple companies and generate bulk INSERT statement"""
    print(f"Processing {len(companies)} companies.")
    print(f"Connecting to MCP server...")
    
    # Create client with in-memory transport using imported server
    client = Client(mcp)
    
    try:
        # Use async context manager for the client
        async with client:
            print("Connected to MCP server.")
            
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Call the appropriate tool based on number of companies
            if len(companies) == 1:
                # Single company - use original tool
                company = companies[0]
                print(f"Calling process_financial_data tool for {company['company_name']}...")
                print("Server logs will appear below:")
                print("-" * 60)
                
                result = await client.call_tool(
                    "process_financial_data",
                    {
                        "company_name": company["company_name"],
                        "year": company["year"],
                        "cik": company["cik"],
                        "model": model
                    }
                )
                
                print("-" * 60)
                print("Financial data processing completed.")
                print("=" * 80)
                print("RESULT:")
                print("=" * 80)
            else:
                # Multiple companies - use batch tool
                print(f"Calling process_financial_batch tool for {len(companies)} companies...")
                print("Server logs will appear below:")
                print("-" * 60)
                
                result = await client.call_tool(
                    "process_financial_batch",
                    {
                        "companies": companies,
                        "model": model
                    }
                )
                
                print("-" * 60)
                print("Batch processing completed.")
                print("=" * 80)
                print("BULK INSERT STATEMENT:")
                print("=" * 80)
            
            # Display the result
            print(result[0].text)
            print("=" * 80)
            
    except Exception as e:
        print(f"Error processing companies: {e}")
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
            print(f"Detected CSV headers: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):
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
                        print(f"Warning: Missing company name in row {row_num}, skipping.")
                        continue
                    if not year:
                        print(f"Warning: Missing or invalid year in row {row_num}, skipping.")
                        continue
                    if not cik:
                        print(f"Warning: Missing CIK in row {row_num}, skipping.")
                        continue
                    
                    companies.append({
                        "company_name": company_name,
                        "year": year,
                        "cik": cik
                    })
                    
                except ValueError as e:
                    print(f"Warning: Invalid data in row {row_num}: {e}, skipping.")
                    continue
                except Exception as e:
                    print(f"Warning: Error processing row {row_num}: {e}, skipping.")
                    continue
        
        print(f"Loaded {len(companies)} valid companies from CSV.")
        return companies
        
    except FileNotFoundError:
        print(f"Error: CSV file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Financial Data Extraction Client using Proxy Architecture",
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
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable is required.")
        print("Please set it with: export OPENROUTER_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Determine processing mode
    if args.csv:
        # Batch processing mode
        companies = load_companies_from_csv(args.csv)
        
        if not companies:
            print("Error: No valid companies found in CSV file.")
            sys.exit(1)
        
        print("Financial Data Extraction Client (Batch Mode)")
        print(f"Model: {args.model}")  
        print(f"CSV File: {args.csv}")
        print(f"Total Companies: {len(companies)}")
        print("-" * 80)
        
        # Show preview of companies to be processed
        print("Companies to process:")
        for i, company in enumerate(companies[:5]):  # Show first 5
            print(f"   {i+1}. {company['company_name']} ({company['year']}) - CIK: {company['cik']}")
        if len(companies) > 5:
            print(f"   ... and {len(companies) - 5} more")
        print("-" * 80)
        
        try:
            asyncio.run(process_companies(companies, args.model))
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)
        
    elif args.company and args.year and args.cik:
        # Single company mode
        print("Financial Data Extraction Client (Single Company)")
        print(f"Model: {args.model}")
        print(f"Company: {args.company}")
        print(f"Year: {args.year}")
        print(f"CIK: {args.cik}")
        print("-" * 80)
        
        try:
            asyncio.run(process_company(args.company, args.year, args.cik, args.model))
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)
        
    else:
        print("Error: Must specify either:")
        print("  Single company: --company, --year, and --cik")
        print("  Batch processing: --csv")
        sys.exit(1)

if __name__ == "__main__":
    main()
