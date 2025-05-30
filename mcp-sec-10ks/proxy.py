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
proxy = FastMCP(name="FinancialDataExtractorProxy")

# Initialize OpenAI client with OpenRouter configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@proxy.tool()
async def extract_financial_data(
    company_name: str,
    year: int,
    report_date: str,
    income_statement_markdown: str,
    balance_sheet_markdown: str,
    model: str = "anthropic/claude-3.5-sonnet"
) -> str:
    """Extract financial data using an LLM via OpenRouter API."""
    logger.info(f"Extracting financial data for {company_name} with model: {model}")
    
    try:
        # Check if API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.warning("OPENROUTER_API_KEY not found")
            return f"Error: OPENROUTER_API_KEY not found in environment variables."
        
        # Create the extraction prompt
        prompt = _create_extraction_prompt(
            company_name,
            year,
            report_date,
            income_statement_markdown,
            balance_sheet_markdown
        )

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        # Extract the response
        extracted_data = response.choices[0].message.content.strip()
        logger.info("Financial data extracted successfully")
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error extracting financial data with LLM: {e}")
        return f"Error extracting financial data with LLM: {str(e)}"

@proxy.tool()
async def extract_values_clause(
    company_name: str,
    year: int,
    report_date: str,
    income_statement_markdown: str,
    balance_sheet_markdown: str,
    model: str = "anthropic/claude-3.5-sonnet"
) -> str:
    """Extract financial data as VALUES clause only using an LLM via OpenRouter API."""
    logger.info(f"Extracting VALUES clause for {company_name} with model: {model}")
    
    try:
        # Check if API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.warning("OPENROUTER_API_KEY not found")
            return f"Error: OPENROUTER_API_KEY not found in environment variables."
        
        # Create the VALUES extraction prompt
        prompt = _create_values_extraction_prompt(
            company_name,
            year,
            report_date,
            income_statement_markdown,
            balance_sheet_markdown
        )

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        # Extract the response
        values_clause = response.choices[0].message.content.strip()
        logger.info("VALUES clause extracted successfully")
        
        return values_clause
        
    except Exception as e:
       logger.error(f"Error extracting VALUES clause with LLM: {e}")
       return f"Error extracting VALUES clause with LLM: {str(e)}"

def _create_extraction_prompt(
   company_name: str, 
   fiscal_year: int, 
   report_date: str, 
   income_statement_markdown: str, 
   balance_sheet_markdown: str
) -> str:
   """Creates the prompt for LLM to extract financial data"""
   return f"""Extract financial data from the income statement and balance sheet below and format as a MySQL INSERT statement.

<concepts>
 "Net Revenue" 
 "Cost of Goods" 
 "SGA"
 "Operating Profit" 
 "Net Profit" 
 "Inventory" 
 "Current Assets" 
 "Total Assets" 
 "Current Liabilities" 
 "Total Shareholder Equity"
 "Total Liabilities and Shareholder Equity"
</concepts>

<income_statement>
{income_statement_markdown}
</income_statement>

<balance_sheet>
{balance_sheet_markdown}
</balance_sheet>

The target table structure is:
INSERT INTO financials (company_name, year, reportDate, `Net Revenue`, `Cost of Goods`, `Gross Margin`, `SGA`, `Operating Profit`, `Net Profit`, `Inventory`, `Current Assets`, `Total Assets`, `Current Liabilities`, `Liabilities`, `Total Shareholder Equity`, `Total Liabilities and Shareholder Equity`)
VALUES (...);

Rules:
- Company name: "{company_name}"
- Fiscal year: {fiscal_year}
- Report date: '{report_date}'
- Report values in thousands (divide by 1000)
- SGA and Cost of Goods as positive values
- Operating/Net Profit can be negative
- Use NULL for any missing values

Computed fields (calculate these):
- Gross Margin = Net Revenue - Cost of Goods (if both available, otherwise NULL)
- Liabilities = Total Assets - Total Shareholder Equity (always calculate this)

Important: 
- If Cost of Goods is NULL, then Gross Margin must be NULL
- If any component for Liabilities calculation is NULL, then Liabilities = NULL
"""

def _create_values_extraction_prompt(
   company_name: str, 
   fiscal_year: int, 
   report_date: str, 
   income_statement_markdown: str, 
   balance_sheet_markdown: str
) -> str:
   """Creates the prompt for LLM to extract financial data as VALUES clause only"""
   return f"""Extract financial data from the income statement and balance sheet below and return ONLY the VALUES clause for a MySQL INSERT statement.

<concepts>
 "Net Revenue" 
 "Cost of Goods" 
 "SGA"
 "Operating Profit" 
 "Net Profit" 
 "Inventory" 
 "Current Assets" 
 "Total Assets" 
 "Current Liabilities" 
 "Total Shareholder Equity"
 "Total Liabilities and Shareholder Equity"
</concepts>

<income_statement>
{income_statement_markdown}
</income_statement>

<balance_sheet>
{balance_sheet_markdown}
</balance_sheet>

The target table structure is:
(company_name, year, reportDate, `Net Revenue`, `Cost of Goods`, `Gross Margin`, `SGA`, `Operating Profit`, `Net Profit`, `Inventory`, `Current Assets`, `Total Assets`, `Current Liabilities`, `Liabilities`, `Total Shareholder Equity`, `Total Liabilities and Shareholder Equity`)

Return ONLY the VALUES clause in this format:
('CompanyName', fiscal_year, 'report_date', net_revenue, cost_of_goods, gross_margin, sga, operating_profit, net_profit, inventory, current_assets, total_assets, current_liabilities, liabilities, total_shareholder_equity, total_liabilities_and_equity)

Rules:
- Company name: "{company_name}"
- Fiscal year: {fiscal_year}
- Report date: '{report_date}'
- Report values in thousands (divide by 1000)
- SGA and Cost of Goods as positive values
- Operating/Net Profit can be negative
- Use NULL for any missing values

Computed fields (calculate these):
- Gross Margin = Net Revenue - Cost of Goods (if both available, otherwise NULL)
- Liabilities = Total Assets - Total Shareholder Equity (always calculate this)

Important: 
- If Cost of Goods is NULL, then Gross Margin must be NULL
- If any component for Liabilities calculation is NULL, then Liabilities = NULL
- Respond with ONLY the VALUES clause, no other text
"""

if __name__ == "__main__":
   logger.info("Starting FinancialDataExtractorProxy")
   proxy.run()

