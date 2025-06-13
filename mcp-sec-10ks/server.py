#!/usr/bin/env python3
"""
Simplified Financial Data Processing Server
"""
import logging
import sys
from fastmcp import FastMCP
from edgar import Company, set_identity

# Configure logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Suppress httpx info logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set identity for edgartools
set_identity("Calvin Williamson calvin_williamson@fitnyc.edu")

# Create the main MCP server
mcp = FastMCP(name="FinancialDataServer")

async def _get_filing_data(company_name: str, year: int, cik: str):
    """
    Common helper function to retrieve filing data for a company and year
    
    Returns:
        tuple: (full_filing, selected_filing) or raises exception
    """
    logger.info(f"Starting financial data retrieval for {company_name}")
    logger.info(f"Parameters: CIK={cik}, Fiscal Year={year}")
    
    # Clean the CIK input
    cleaned_cik = "".join(filter(str.isdigit, cik))
    logger.info(f"Cleaned CIK: {cleaned_cik}")
    
    # Get the company object
    logger.info("Fetching company information from SEC...")
    company = Company(cleaned_cik)
    
    # Get 10-K filings
    logger.info("Retrieving 10-K filings...")
    filings = company.get_filings(form="10-K")
    logger.info(f"Found {len(filings)} total 10-K filings")
    
    if not filings:
        logger.error(f"No 10-K filings found for CIK {cleaned_cik}")
        raise ValueError(f"No 10-K filings found for CIK {cleaned_cik}")
    
    # Find the appropriate filing for the requested fiscal year
    logger.info(f"Searching for fiscal year {year} filing...")
    logger.info(f"Logic: FY {year} can have Period in early {year+1} (Jan-Jul) or late {year} (Aug-Dec)")
    selected_filing = None
    
    for i, filing in enumerate(filings):
        try:
            period_str = filing.period_of_report
            filed_str = filing.filing_date
            logger.info(f"  Filing {i+1}: Period={period_str}, Filed={filed_str}")
            
            # Handle both YYYYMMDD and YYYY-MM-DD formats
            period_year = None
            period_month = None
            
            if len(period_str) == 8 and period_str.isdigit():
                # Format: YYYYMMDD
                period_year = int(period_str[:4])
                period_month = int(period_str[4:6])
            elif len(period_str) == 10 and period_str.count('-') == 2:
                # Format: YYYY-MM-DD
                parts = period_str.split('-')
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    period_year = int(parts[0])
                    period_month = int(parts[1])
            else:
                logger.info(f"    Unrecognized period format: {period_str}")
                continue
            
            if period_year and period_month:
                # Determine which fiscal year this period represents
                if period_month <= 7:  # Jan-Jul: represents previous fiscal year
                    fiscal_year_represented = period_year - 1
                    logger.info(f"    Period {period_str} (month {period_month:02d}) -> FY {fiscal_year_represented}")
                else:  # Aug-Dec: represents same fiscal year
                    fiscal_year_represented = period_year
                    logger.info(f"    Period {period_str} (month {period_month:02d}) -> FY {fiscal_year_represented}")
                
                if fiscal_year_represented == year:
                    selected_filing = filing
                    logger.info(f"MATCH! Selected filing for FY {year}: Period={period_str}")
                    break
                else:
                    logger.info(f"    FY {fiscal_year_represented} != requested FY {year}")
                    
        except Exception as filing_error:
            logger.info(f"Warning: Error checking filing {i+1}: {filing_error}")
            continue
    
    if not selected_filing:
        logger.error(f"No filing found for fiscal year {year}")
        raise ValueError(f"No 10-K filing found for fiscal year {year}")
    
    # Get the full filing object
    logger.info("Loading full filing document...")
    full_filing = selected_filing.obj()
    
    return full_filing, selected_filing

@mcp.tool()
async def process_financial_data_from_sec(
    company_name: str, 
    year: int, 
    cik: str
) -> str:
    """
    Extract income statement and balance sheet with extraction prompt for a company's financial data
    
    Args:
        company_name: Name of the company
        year: Fiscal year to extract
        cik: Company's CIK number
        
    Returns:
        Single string containing extraction prompt and both financial statements
    """
    try:
        # Get filing data using shared helper
        full_filing, selected_filing = await _get_filing_data(company_name, year, cik)
        
        # Get financial statements
        logger.info("Extracting income statement...")
        income_statement = full_filing.income_statement.to_dataframe()
        logger.info(f"Income statement extracted ({len(income_statement)} rows)")
        
        logger.info("Extracting balance sheet...")
        balance_sheet = full_filing.balance_sheet.to_dataframe()
        logger.info(f"Balance sheet extracted ({len(balance_sheet)} rows)")
        
        # Format as markdown
        income_result = income_statement.to_markdown()
        balance_result = balance_sheet.to_markdown()
        
        # Combine both statements with clear delimiters and instructions
        extraction_prompt = f"""Can you find the financial data included here for {company_name}, {year}.

Then get income statement and find the latest year's values on it:
- "Net Revenue" 
- "Cost of Goods" (report as positive value)
- "SGA" (report as positive value)
- "Operating Profit" 
- "Net Profit" 

Then on the balance sheet find these values on it:
- "Inventory" 
- "Current Assets" 
- "Total Assets" 
- "Current Liabilities" 
- "Total Shareholder Equity"
- "Total Liabilities and Shareholder Equity"

Can you return them in a markdown table rounded to the thousands using my names for them and add two computed fields, Gross Margin and Liabilities:
- Gross Margin = Net Revenue - Cost of Goods (if both available, otherwise NULL)
- Liabilities = Total Assets - Total Shareholder Equity (always calculate this)

Here's the final list of fields to extract:
company_name, year, reportDate, Net Revenue, Cost of Goods, Gross Margin, SGA, Operating Profit, Net Profit, Inventory, Current Assets, Total Assets, Current Liabilities, Liabilities, Total Shareholder Equity, Total Liabilities and Shareholder Equity

---

# INCOME STATEMENT

{income_result}

# BALANCE SHEET

{balance_result}"""
        
        logger.info("Financial statement extraction completed successfully.")
        return extraction_prompt
        
    except Exception as e:
        logger.error(f"Error processing financial data: {str(e)}")
        return f"Error processing financial data: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting FinancialDataServer")
    mcp.run()
