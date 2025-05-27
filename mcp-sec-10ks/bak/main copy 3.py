#!/usr/bin/env python3
"""
Enhanced MCP Server with Batch Processing and Bulk INSERT Support
"""
from fastmcp import FastMCP, Context
from edgar import Company, set_identity
import pandas as pd
from typing import List, Dict, Any
import asyncio

# Set identity for edgartools
set_identity("Calvin Williamson calvin_williamson@fitnyc.edu")

# Create the MCP server
mcp = FastMCP("mcp-sec-10ks")

@mcp.tool()
async def process_financial_batch(
    companies: List[Dict[str, Any]],
    ctx: Context
) -> str:
    """
    Process a batch of companies and generate a bulk INSERT statement
    """
    try:
        await ctx.info(f"Starting batch processing of {len(companies)} companies")
        
        all_values = []
        successful_companies = []
        failed_companies = []
        
        for i, company_info in enumerate(companies):
            company_name = company_info.get("company_name")
            year = company_info.get("year") 
            cik = company_info.get("cik")
            
            await ctx.info(f"Processing {i+1}/{len(companies)}: {company_name} ({year})")
            
            try:
                # Get the financial data for this company
                values_clause = await _process_single_company(company_name, year, cik, ctx)
                
                if values_clause and values_clause.strip():
                    all_values.append(values_clause.strip())
                    successful_companies.append(f"{company_name} ({year})")
                    await ctx.info(f"✅ Successfully processed {company_name} ({year})")
                else:
                    failed_companies.append(f"{company_name} ({year}) - No data returned")
                    await ctx.error(f"❌ No data returned for {company_name} ({year})")
                    
            except Exception as e:
                failed_companies.append(f"{company_name} ({year}) - {str(e)}")
                await ctx.error(f"❌ Failed to process {company_name} ({year}): {e}")
                continue
        
        # Generate bulk INSERT statement
        if all_values:
            bulk_insert = _generate_bulk_insert(all_values)
            
            # Generate summary
            summary = f"""
-- BATCH PROCESSING SUMMARY
-- ========================
-- Total companies requested: {len(companies)}
-- Successfully processed: {len(successful_companies)}
-- Failed: {len(failed_companies)}
--
-- Successful companies:
{chr(10).join([f"-- ✅ {company}" for company in successful_companies])}
--
"""
            if failed_companies:
                summary += f"""-- Failed companies:
{chr(10).join([f"-- ❌ {company}" for company in failed_companies])}
--
"""
            
            summary += f"""-- BULK INSERT STATEMENT
-- =====================
{bulk_insert}
"""
            
            await ctx.info(f"Batch processing completed: {len(successful_companies)}/{len(companies)} successful")
            return summary
        else:
            error_msg = f"No companies were successfully processed. Failures:\n" + "\n".join(failed_companies)
            await ctx.error(error_msg)
            return error_msg
            
    except Exception as e:
        await ctx.error(f"Batch processing failed: {e}")
        return f"Batch processing failed: {e}"

async def _process_single_company(
    company_name: str, 
    year: int, 
    cik: str,
    ctx: Context
) -> str:
    """
    Process a single company and return just the VALUES clause
    """
    try:
        # Clean the CIK input
        cleaned_cik = "".join(filter(str.isdigit, cik))
        
        # Get the company and filing
        company = Company(cleaned_cik)
        filing = _get_10k_filing_for_year(company, year)
        
        if not filing:
            await ctx.error(f"No 10-K filing found for CIK {cleaned_cik} in year {year}")
            return ""
        
        # Get income statement and balance sheet as markdown
        income_statement = filing.income_statement.to_dataframe()
        income_statement_markdown = income_statement.to_markdown()
        
        balance_sheet = filing.balance_sheet.to_dataframe()
        balance_sheet_markdown = balance_sheet.to_markdown()
        
        # Create the extraction prompt for VALUES only
        extraction_prompt = _create_values_extraction_prompt(
            company_name, 
            income_statement_markdown, 
            balance_sheet_markdown
        )
        
        # Use sampling to request LLM processing
        result = await ctx.sample(extraction_prompt)
        
        # Extract just the VALUES clause from the result
        values_clause = _extract_values_clause(result.text)
        
        return values_clause
        
    except Exception as e:
        await ctx.error(f"Error processing {company_name}: {e}")
        raise

def _extract_values_clause(llm_response: str) -> str:
    """
    Extract just the VALUES clause from LLM response
    """
    # Look for VALUES clause in the response
    response_lower = llm_response.lower()
    
    # Find VALUES keyword
    values_start = response_lower.find("values")
    if values_start == -1:
        # Try to find parentheses that might contain the data
        paren_start = llm_response.find("(")
        if paren_start != -1:
            return llm_response[paren_start:].strip()
        return llm_response.strip()
    
    # Extract from VALUES onward, but clean it up
    values_part = llm_response[values_start:].strip()
    
    # Remove "VALUES" keyword, we'll add it back in bulk insert
    if values_part.lower().startswith("values"):
        values_part = values_part[6:].strip()
    
    # Remove trailing semicolon if present
    values_part = values_part.rstrip(";").strip()
    
    return values_part

def _generate_bulk_insert(values_list: List[str]) -> str:
    """
    Generate a bulk INSERT statement from list of VALUES clauses
    """
    table_definition = """INSERT INTO financials (
  company_name, 
  year, 
  reportDate, 
  `Net Revenue`, 
  `Cost of Goods`, 
  `SGA`, 
  `Operating Profit`, 
  `Net Profit`, 
  `Inventory`, 
  `Current Assets`, 
  `Total Assets`, 
  `Current Liabilities`, 
  `Total Shareholder Equity`, 
  `Total Liabilities and Shareholder Equity`
)
VALUES"""
    
    # Join all VALUES clauses with commas
    all_values = ",\n".join([f"  {values}" for values in values_list])
    
    return f"{table_definition}\n{all_values};"

@mcp.tool()
async def process_financial_data(
    company_name: str, 
    year: int, 
    cik: str,
    ctx: Context
) -> str:
    """
    Downloads 10-K financial data and uses sampling to extract standardized financial fields
    (Original single-company function preserved for backward compatibility)
    """
    try:
        # Clean the CIK input
        cleaned_cik = "".join(filter(str.isdigit, cik))
        
        await ctx.info(f"Processing financial data for {company_name} ({cleaned_cik}) for year {year}")
        
        # Get the company and filing
        company = Company(cleaned_cik)
        filing = _get_10k_filing_for_year(company, year)
        
        if not filing:
            return f"No 10-K filing found for CIK {cleaned_cik} in year {year}."
        
        # Get income statement and balance sheet as markdown
        await ctx.info("Downloading income statement...")
        income_statement = filing.income_statement.to_dataframe()
        income_statement_markdown = income_statement.to_markdown()
        
        await ctx.info("Downloading balance sheet...")
        balance_sheet = filing.balance_sheet.to_dataframe()
        balance_sheet_markdown = balance_sheet.to_markdown()
        
        # Create the extraction prompt
        extraction_prompt = _create_extraction_prompt(
            company_name, 
            income_statement_markdown, 
            balance_sheet_markdown
        )
        
        await ctx.info("Requesting LLM to extract financial data...")
        
        # Use sampling to request LLM processing
        result = await ctx.sample(extraction_prompt)
        
        await ctx.info("Financial data extraction completed")
        
        return result.text
        
    except Exception as e:
        await ctx.error(f"Error processing financial data: {e}")
        return f"Error processing financial data: {e}"

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! from MCP sec-10ks"

@mcp.tool()
def get_10k_income_statement(year: int, cik: str) -> str:
    """Gets the income statement sheet as a markdown table for a given year and CIK."""
    cleaned_cik = "".join(filter(str.isdigit, cik))
    company = Company(cleaned_cik)
    try:
        filing = _get_10k_filing_for_year(company, year)
        if filing:
            income_statement = filing.income_statement.to_dataframe()
            return income_statement.to_markdown()
        else:
            return f"No 10-K filing found for CIK {cleaned_cik} in year {year}."
    except Exception as e:
        return f"Error fetching income statement: {e}"

@mcp.tool()
def get_10k_balance_sheet(year: int, cik: str) -> str:
    """Gets the balance sheet as a markdown table for a given year and CIK."""
    cleaned_cik = "".join(filter(str.isdigit, cik))
    company = Company(cleaned_cik)
    try:
        filing = _get_10k_filing_for_year(company, year)
        if filing:
            balance_sheet = filing.balance_sheet.to_dataframe()
            return balance_sheet.to_markdown()
        else:
            return f"No 10-K filing found for CIK {cleaned_cik} in year {year}."
    except Exception as e:
        return f"Error fetching balance sheet: {e}"

def _get_10k_filing_for_year(company: Company, year: int):
    """Helper function to get the 10-K filing for a specific year."""
    filings = company.get_filings(form="10-K")
    for filing in filings:
        filing_year = int(filing.period_of_report[:4])
        if filing_year == year:
            return filing.obj()
    return None

def _create_values_extraction_prompt(company_name: str, income_statement_markdown: str, balance_sheet_markdown: str) -> str:
    """Creates the prompt for LLM to extract financial data as VALUES clause only"""
    return f""" 
Extract financial data from the income statement and balance sheet below and return ONLY the VALUES clause for a MySQL INSERT statement.

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
(company_name, year, reportDate, `Net Revenue`, `Cost of Goods`, `SGA`, `Operating Profit`, `Net Profit`, `Inventory`, `Current Assets`, `Total Assets`, `Current Liabilities`, `Total Shareholder Equity`, `Total Liabilities and Shareholder Equity`)

Return ONLY the VALUES clause in this format:
('CompanyName', year, 'YYYY-MM-DD', value1, value2, value3, ...)

Rules:
- Company name: "{company_name}"
- Report values in thousands (divide by 1000)
- SGA and Cost of Goods as positive values
- Operating/Net Profit can be negative
- Calculate fiscal year from reportDate (before July 1st = previous year, July 1st+ = same year)
- Include the most recent reportDate from the financial statements
- Respond with ONLY the VALUES clause, no other text
"""

def _create_extraction_prompt(company_name: str, income_statement_markdown: str, balance_sheet_markdown: str) -> str:
    """Creates the original prompt for LLM to extract financial data (backward compatibility)"""
    return f""" 
Below is a list of financial concepts (given inside the <concepts> tags) to be
found in the income statement and the balance sheet of a companies 10-K report.

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

Find the concepts and their values in the income statement or the balance
sheet that follow.

The income statement is enclosed in  <income_statment> tags.
The balance sheet is enclosed in <balance_sheet> tags.

Here is the income statement:

<income_statement>
{income_statement_markdown}
</income_statement>

Here is the balance sheet:

<balance_sheet>
{balance_sheet_markdown}
</balance_sheet>

Please return the values in the form of an insert statement for 
the MySql database table with the schema as follows:

CREATE TABLE financials (
  company_name varchar(255) NOT NULL,
  year int NOT NULL,
  reportDate date NOT NULL,
  `Net Revenue` bigint,
  `Cost of Goods` bigint,
  `Gross Margin` bigint DEFAULT NULL,
  `SGA` bigint,
  `Operating Profit` bigint,
  `Net Profit` bigint,
  `Inventory` bigint,
  `Current Assets` bigint,
  `Total Assets` bigint,
  `Current Liabilities` bigint,
  `Liabilities` bigint DEFAULT NULL,
  `Total Shareholder Equity` bigint,
  `Total Liabilities and Shareholder Equity` bigint,
  PRIMARY KEY (company_name,year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin

Provide a number for every concept. Respond only with the insert statement
no other commentary or discussion.

Please report the values in thousands, so you need to divide by 1000 for each
value you return. Also the SGA and Cost of Goods should be returned as positive
if they are negative, but Operating Profit and Net Profit can be negative and
they should retain the sign of the value as reported originally.

Also add the reportDate, which is at the top of the column containing the most 
recent data.

Also add the fiscal year (called simply "year") of the data, which will be the
year before the reportDate if the day from the reportDate is June 30th or
before, otherwise if the day of the reportDate is July 1st or after, then the
year will be the same year as the year of the reportDate

The company name should be "{company_name}".
"""

if __name__ == "__main__":
    mcp.run()