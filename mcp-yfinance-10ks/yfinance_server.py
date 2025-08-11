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

async def _get_financial_data(company_name: str, ticker_symbol: str):
    """
    Common helper function to retrieve financial data for a company from Yahoo Finance.
    It validates the ticker by fetching financial statements directly, avoiding ticker.info.
    
    Returns:
        tuple: (income_statement, balance_sheet) or raises exception
    """
    logger.info(f"Starting Yahoo Finance data retrieval for {company_name}")
    logger.info(f"Parameters: Ticker={ticker_symbol}")
    
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
    
    logger.info("Financial data retrieved successfully")
    
    return income_statement, balance_sheet

@mcp.tool()
async def process_financial_data_from_yahoo(
    company_name: str, 
    ticker_symbol: str
) -> str:
    """
    Extract income statement and balance sheet with extraction prompt for a company's financial data from Yahoo Finance
    
    Args:
        company_name: Name of the company
        ticker_symbol: Company's ticker symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        Single string containing extraction prompt and both financial statements
    """
    try:
        # Get financial data using shared helper
        income_statement, balance_sheet = await _get_financial_data(company_name, ticker_symbol)
        
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
        extraction_prompt = f"""Extract financial data for {company_name} from the statements below.

INSTRUCTIONS:
1. The data contains multiple columns representing different fiscal periods (typically 4 years of data)
2. Each column header shows the fiscal period end date (e.g., "2025-01-31", "2024-01-31", etc.)
3. Choose the most recent fiscal period (leftmost column) OR specify which year you're interested in
4. Extract the following fields from your chosen period:

FROM INCOME STATEMENT:
- "Net Revenue" (may be labeled as "Total Revenue", "Operating Revenue", etc.)
- "Cost of Goods" (may be labeled as "Cost Of Revenue", report as positive value)
- "SGA" (may be labeled as "Selling General And Administration", report as positive value)
- "Operating Profit" (may be labeled as "Operating Income", "Total Operating Income As Reported")
- "Net Profit" (may be labeled as "Net Income", "Net Income Common Stockholders")

FROM BALANCE SHEET:
- "Inventory"
- "Current Assets" 
- "Total Assets"
- "Current Liabilities"
- "Total Shareholder Equity" (may be labeled as "Stockholders Equity", "Common Stock Equity")
- "Total Liabilities and Shareholder Equity"

COMPUTED FIELDS (add these):
- Gross Margin = Net Revenue - Cost of Goods (if both available, otherwise NULL)
- Liabilities = Total Assets - Total Shareholder Equity (always calculate this)

OUTPUT FORMAT:
Return a markdown table with values rounded to thousands and include ALL these fields:
company_name, reportDate, Net Revenue, Cost of Goods, Gross Margin, SGA, Operating Profit, Net Profit, Inventory, Current Assets, Total Assets, Current Liabilities, Liabilities, Total Shareholder Equity, Total Liabilities and Shareholder Equity

CRITICAL: For reportDate, use the exact fiscal period end date from the column header you selected (e.g., "2025-01-31").

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
