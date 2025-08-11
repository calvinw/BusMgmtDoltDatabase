#!/usr/bin/env python3

import asyncio
import sys
import logging
from yfinance_server import _get_financial_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

async def test_macys():
    try:
        # Get financial data using the modified function
        income_statement, balance_sheet = await _get_financial_data("Macy's", "M")
        
        # Format as markdown
        if not income_statement.empty:
            income_result = income_statement.to_markdown()
        else:
            income_result = "No income statement data available"
            
        if not balance_sheet.empty:
            balance_result = balance_sheet.to_markdown()
        else:
            balance_result = "No balance sheet data available"
        
        # Create the full extraction prompt
        extraction_prompt = f"""Extract financial data for Macy's from the statements below.

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
        
        print("SUCCESS: Full extraction prompt created")
        print("="*50)
        print(extraction_prompt)
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_macys())