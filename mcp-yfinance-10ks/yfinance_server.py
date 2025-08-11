#!/usr/bin/env python3
"""
Yahoo Finance Financial Data Processing Server
"""
import logging
import sys
from datetime import datetime
from fastmcp import FastMCP
import yfinance as yf
import pandas as pd

# Configure logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create the main MCP server
mcp = FastMCP(name="YahooFinanceDataServer")

async def _get_financial_data(company_name: str, year: int, ticker_symbol: str):
    """
    Common helper function to retrieve financial data for a company and year from Yahoo Finance.
    It validates the ticker by fetching financial statements directly, avoiding ticker.info.
    
    Returns:
        tuple: (income_statement, balance_sheet, selected_column) or raises exception
    """
    logger.info(f"Starting Yahoo Finance data retrieval for {company_name}")
    logger.info(f"Parameters: Ticker={ticker_symbol}, Fiscal Year={year}")
    
    # Clean the ticker symbol input
    cleaned_ticker = ticker_symbol.upper().strip()
    logger.info(f"Cleaned ticker: {cleaned_ticker}")
    
    # Get the ticker object
    ticker = yf.Ticker(cleaned_ticker)
    
    # Get financial statements
    logger.info("Retrieving financial statements...")
    try:
        # Get annual financials (income statement) and balance sheet
        income_statement = ticker.financials
        balance_sheet = ticker.balance_sheet
        
        # Validate the ticker by checking if any financial data was returned.
        # This is more reliable than using ticker.info for international symbols.
        if income_statement.empty and balance_sheet.empty:
            logger.error(f"No financial data found for ticker {cleaned_ticker}. It may be invalid, delisted, or not supported.")
            raise ValueError(f"No financial data found for ticker symbol: {cleaned_ticker}")
            
        if income_statement is None or income_statement.empty:
            logger.warning("No income statement data available")
            income_statement = pd.DataFrame()
        else:
            logger.info(f"Income statement retrieved ({len(income_statement.columns)} periods)")
        
        if balance_sheet is None or balance_sheet.empty:
            logger.warning("No balance sheet data available")
            balance_sheet = pd.DataFrame()
        else:
            logger.info(f"Balance sheet retrieved ({len(balance_sheet.columns)} periods)")
            
    except Exception as e:
        logger.error(f"Error retrieving financial statements for {cleaned_ticker}: {str(e)}")
        raise ValueError(f"Could not retrieve financial statements for {cleaned_ticker}: {str(e)}")
    
    # Check if we have data for the requested fiscal year
    logger.info(f"Checking for fiscal year {year} data...")
    logger.info(f"Logic: FY {year} can have Period ending in early {year+1} (Jan-Jul) or late {year} (Aug-Dec)")
    
    selected_column = None
    target_year_found = False
    
    if not income_statement.empty:
        logger.info("Analyzing available financial statement periods...")
        
        for i, col in enumerate(income_statement.columns):
            try:
                # Extract date information from column (pandas Timestamp)
                if hasattr(col, 'year') and hasattr(col, 'month'):
                    period_year = col.year
                    period_month = col.month
                    period_str = col.strftime('%Y-%m-%d')
                    
                    logger.info(f"  Period {i+1}: {period_str} (year {period_year}, month {period_month:02d})")
                    
                    # Determine which fiscal year this period represents
                    if period_month <= 7:  # Jan-Jul: represents previous fiscal year
                        fiscal_year_represented = period_year - 1
                        logger.info(f"    Period {period_str} (month {period_month:02d}) -> FY {fiscal_year_represented}")
                    else:  # Aug-Dec: represents same fiscal year
                        fiscal_year_represented = period_year
                        logger.info(f"    Period {period_str} (month {period_month:02d}) -> FY {fiscal_year_represented}")
                    
                    if fiscal_year_represented == year:
                        selected_column = col
                        target_year_found = True
                        logger.info(f"MATCH! Selected period for FY {year}: {period_str}")
                        break
                    else:
                        logger.info(f"    FY {fiscal_year_represented} != requested FY {year}")
                        
            except Exception as period_error:
                logger.info(f"Warning: Error checking period {i+1}: {period_error}")
                continue
    
    if not target_year_found and not income_statement.empty:
        logger.warning(f"No period found for fiscal year {year}. Using most recent available data.")
        selected_column = income_statement.columns[0]  # Most recent is typically first column
        logger.info(f"Selected most recent period: {selected_column.strftime('%Y-%m-%d') if selected_column else 'N/A'}")
    
    return income_statement, balance_sheet, selected_column

@mcp.tool()
async def process_financial_data_from_yahoo(
    company_name: str, 
    year: int, 
    ticker_symbol: str
) -> str:
    """
    Extract income statement and balance sheet with extraction prompt for a company's financial data from Yahoo Finance
    
    Args:
        company_name: Name of the company
        year: Fiscal year to extract (note: Yahoo Finance only provides ~4 years of data)
        ticker_symbol: Company's ticker symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        Single string containing extraction prompt and both financial statements
    """
    try:
        # Get financial data using shared helper
        income_statement, balance_sheet, selected_column = await _get_financial_data(company_name, year, ticker_symbol)
        
        # Format as markdown
        if not income_statement.empty:
            income_result = income_statement.to_markdown()
            logger.info("Income statement formatted successfully")
        else:
            income_result = "No income statement data available"
            logger.warning("No income statement data to format")
            
        if not balance_sheet.empty:
            balance_result = balance_sheet.to_markdown()
            logger.info("Balance sheet formatted successfully")
        else:
            balance_result = "No balance sheet data available"
            logger.warning("No balance sheet data to format")
        
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

CRITICAL: For the reportDate field, use the FISCAL YEAR END DATE from the financial statement period headers. This is the leftmost/most recent date column in the income statement or balance sheet (e.g., if columns show "2025-02-01 | 2024-02-03 | 2023-01-28", use "2025-02-01" as the reportDate). DO NOT use filing dates, publication dates, or any other administrative dates - only the actual fiscal period end date from the statement headers.

Here's the final list of fields to extract:
company_name, year, reportDate, Net Revenue, Cost of Goods, Gross Margin, SGA, Operating Profit, Net Profit, Inventory, Current Assets, Total Assets, Current Liabilities, Liabilities, Total Shareholder Equity, Total Liabilities and Shareholder Equity

---

# INCOME STATEMENT

{income_result}

# BALANCE SHEET

{balance_result}"""
        
        logger.info("Yahoo Finance financial statement extraction completed successfully.")
        return extraction_prompt
        
    except Exception as e:
        logger.error(f"Error processing Yahoo Finance financial data: {str(e)}")
        return f"Error processing Yahoo Finance financial data: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting YahooFinanceDataServer")
    mcp.run()
