#!/usr/bin/env python3
"""
Simplified MCP Server with FastMCP approach for SEC 10-K Financial Data Extraction
"""
from fastmcp import FastMCP, Context
from edgar import Company, set_identity
import pandas as pd

# Set identity for edgartools
set_identity("Calvin Williamson calvin_williamson@fitnyc.edu")

# Create the MCP server
mcp = FastMCP("mcp-sec-10ks")

@mcp.tool()
async def process_financial_data(
    company_name: str, 
    year: int, 
    cik: str,
    ctx: Context
) -> str:
    """
    Process a single company's financial data with detailed logging
    """
    await ctx.info(f"🏢 Starting financial data processing for {company_name}")
    await ctx.info(f"📊 Parameters: CIK={cik}, Fiscal Year={year}")
    
    try:
        # Clean the CIK input
        cleaned_cik = "".join(filter(str.isdigit, cik))
        await ctx.info(f"🔢 Cleaned CIK: {cleaned_cik}")
        
        # Get the company object
        await ctx.info("🔍 Fetching company information from SEC...")
        company = Company(cleaned_cik)
        
        # Get 10-K filings
        await ctx.info("📋 Retrieving 10-K filings...")
        filings = company.get_filings(form="10-K")
        await ctx.info(f"📄 Found {len(filings)} total 10-K filings")
        
        if not filings:
            await ctx.error(f"❌ No 10-K filings found for CIK {cleaned_cik}")
            return f"No 10-K filings found for CIK {cleaned_cik}"
        
        # Find the appropriate filing for the requested fiscal year
        await ctx.info(f"🔎 Searching for fiscal year {year} filing...")
        await ctx.info(f"📋 Logic: FY {year} can have Period in early {year+1} (Jan-Jul) or late {year} (Aug-Dec)")
        selected_filing = None
        
        for i, filing in enumerate(filings):
            try:
                period_str = filing.period_of_report
                filed_str = filing.filing_date
                await ctx.info(f"  📅 Filing {i+1}: Period={period_str}, Filed={filed_str}")
                
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
                    await ctx.info(f"    ⚠️  Unrecognized period format: {period_str}")
                    continue
                
                if period_year and period_month:
                    # Determine which fiscal year this period represents
                    if period_month <= 7:  # Jan-Jul: represents previous fiscal year
                        fiscal_year_represented = period_year - 1
                        await ctx.info(f"    📊 Period {period_str} (month {period_month:02d}) → FY {fiscal_year_represented}")
                    else:  # Aug-Dec: represents same fiscal year
                        fiscal_year_represented = period_year
                        await ctx.info(f"    📊 Period {period_str} (month {period_month:02d}) → FY {fiscal_year_represented}")
                    
                    if fiscal_year_represented == year:
                        selected_filing = filing
                        await ctx.info(f"✅ MATCH! Selected filing for FY {year}: Period={period_str}")
                        break
                    else:
                        await ctx.info(f"    ❌ FY {fiscal_year_represented} ≠ requested FY {year}")
                        
            except Exception as filing_error:
                await ctx.info(f"⚠️  Error checking filing {i+1}: {filing_error}")
                continue
        
        if not selected_filing:
            await ctx.error(f"❌ No filing found for fiscal year {year}")
            return f"No 10-K filing found for fiscal year {year}"
        
        # Get the full filing object
        await ctx.info("📖 Loading full filing document...")
        full_filing = selected_filing.obj()
        
        # Get financial statements
        await ctx.info("💰 Extracting income statement...")
        income_statement = full_filing.income_statement.to_dataframe()
        income_statement_markdown = income_statement.to_markdown()
        await ctx.info(f"✅ Income statement extracted ({len(income_statement)} rows)")
        
        await ctx.info("⚖️  Extracting balance sheet...")
        balance_sheet = full_filing.balance_sheet.to_dataframe()
        balance_sheet_markdown = balance_sheet.to_markdown()
        await ctx.info(f"✅ Balance sheet extracted ({len(balance_sheet)} rows)")
        
        # Format the report date
        report_date = selected_filing.filing_date
        if isinstance(report_date, str) and len(report_date) == 8:
            formatted_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
        else:
            formatted_date = str(report_date)
        
        await ctx.info(f"📅 Report date: {formatted_date}")
        
        # Create the extraction prompt
        await ctx.info("📝 Preparing financial data extraction prompt...")
        extraction_prompt = _create_extraction_prompt(
            company_name,
            year,
            formatted_date,
            income_statement_markdown,
            balance_sheet_markdown
        )
        
        # Use sampling to request LLM processing
        await ctx.info("🤖 Requesting LLM to extract financial data...")
        result = await ctx.sample(extraction_prompt, max_tokens=4000, temperature=0.1)
        
        response_length = len(result.text) if result.text else 0
        await ctx.info(f"✅ LLM processing completed ({response_length} characters)")
        
        if not result.text or response_length == 0:
            await ctx.error("❌ Empty response received from LLM")
            return "Error: Empty response from LLM"
        
        await ctx.info("🎯 Financial data extraction completed successfully")
        return result.text
        
    except Exception as e:
        await ctx.error(f"❌ Error processing financial data: {str(e)}")
        return f"Error processing financial data: {str(e)}"

@mcp.tool()
async def process_financial_batch(
    companies: list,
    ctx: Context
) -> str:
    """
    Process a batch of companies and generate a bulk INSERT statement
    """
    await ctx.info(f"🚀 Starting batch processing of {len(companies)} companies")
    
    all_values = []
    successful_companies = []
    failed_companies = []
    
    for i, company_info in enumerate(companies):
        company_name = company_info.get("company_name")
        year = company_info.get("year") 
        cik = company_info.get("cik")
        
        await ctx.info(f"📊 Processing {i+1}/{len(companies)}: {company_name} ({year})")
        
        try:
            # Process this single company
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
    
    # Generate summary and bulk INSERT statement
    if all_values:
        bulk_insert = _generate_bulk_insert(all_values)
        
        summary = f"""-- BATCH PROCESSING SUMMARY
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
        
        await ctx.info(f"🎯 Batch processing completed: {len(successful_companies)}/{len(companies)} successful")
        return summary
    else:
        error_msg = f"No companies were successfully processed. Failures:\n" + "\n".join(failed_companies)
        await ctx.error(error_msg)
        return error_msg

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
        
        # Get the company object
        company = Company(cleaned_cik)
        
        # Get 10-K filings
        filings = company.get_filings(form="10-K")
        
        if not filings:
            await ctx.error(f"No 10-K filings found for CIK {cleaned_cik}")
            return ""
        
        # Find the appropriate filing for the requested fiscal year
        selected_filing = None
        
        for filing in filings:
            try:
                period_str = filing.period_of_report
                
                # Handle both YYYYMMDD and YYYY-MM-DD formats
                period_year = None
                period_month = None
                
                if len(period_str) == 8 and period_str.isdigit():
                    period_year = int(period_str[:4])
                    period_month = int(period_str[4:6])
                elif len(period_str) == 10 and period_str.count('-') == 2:
                    parts = period_str.split('-')
                    if len(parts) == 3 and all(part.isdigit() for part in parts):
                        period_year = int(parts[0])
                        period_month = int(parts[1])
                else:
                    continue
                
                if period_year and period_month:
                    # Determine which fiscal year this period represents
                    if period_month <= 7:  # Jan-Jul: represents previous fiscal year
                        fiscal_year_represented = period_year - 1
                    else:  # Aug-Dec: represents same fiscal year
                        fiscal_year_represented = period_year
                    
                    if fiscal_year_represented == year:
                        selected_filing = filing
                        break
                        
            except Exception:
                continue
        
        if not selected_filing:
            await ctx.error(f"No filing found for fiscal year {year}")
            return ""
        
        # Get the full filing object
        full_filing = selected_filing.obj()
        
        # Get financial statements
        income_statement = full_filing.income_statement.to_dataframe()
        income_statement_markdown = income_statement.to_markdown()
        
        balance_sheet = full_filing.balance_sheet.to_dataframe()
        balance_sheet_markdown = balance_sheet.to_markdown()
        
        # Format the report date
        report_date = selected_filing.filing_date
        if isinstance(report_date, str) and len(report_date) == 8:
            formatted_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
        elif isinstance(report_date, str) and len(report_date) == 10:
            formatted_date = report_date
        else:
            formatted_date = str(report_date)
        
        # Create the VALUES extraction prompt
        extraction_prompt = _create_values_extraction_prompt(
            company_name,
            year,
            formatted_date,
            income_statement_markdown,
            balance_sheet_markdown
        )
        
        # Use sampling to request LLM processing
        result = await ctx.sample(extraction_prompt, max_tokens=1000, temperature=0.1)
        
        if not result.text:
            await ctx.error("Empty response from LLM")
            return ""
        
        # Extract just the VALUES clause from the result
        values_clause = _extract_values_clause(result.text)
        return values_clause
        
    except Exception as e:
        await ctx.error(f"Error processing {company_name}: {str(e)}")
        return ""

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

def _generate_bulk_insert(values_list: list) -> str:
    """
    Generate a bulk INSERT statement from list of VALUES clauses
    """
    table_definition = """INSERT INTO financials (
  company_name, 
  year, 
  reportDate, 
  `Net Revenue`, 
  `Cost of Goods`, 
  `Gross Margin`,
  `SGA`, 
  `Operating Profit`, 
  `Net Profit`, 
  `Inventory`, 
  `Current Assets`, 
  `Total Assets`, 
  `Current Liabilities`, 
  `Liabilities`,
  `Total Shareholder Equity`, 
  `Total Liabilities and Shareholder Equity`
)
VALUES"""
    
    # Join all VALUES clauses with commas
    all_values = ",\n".join([f"  {values}" for values in values_list])
    
    # Add ON DUPLICATE KEY UPDATE clause
    on_duplicate = """ON DUPLICATE KEY UPDATE
  reportDate = VALUES(reportDate),
  `Net Revenue` = VALUES(`Net Revenue`),
  `Cost of Goods` = VALUES(`Cost of Goods`),
  `Gross Margin` = VALUES(`Gross Margin`),
  `SGA` = VALUES(`SGA`),
  `Operating Profit` = VALUES(`Operating Profit`),
  `Net Profit` = VALUES(`Net Profit`),
  `Inventory` = VALUES(`Inventory`),
  `Current Assets` = VALUES(`Current Assets`),
  `Total Assets` = VALUES(`Total Assets`),
  `Current Liabilities` = VALUES(`Current Liabilities`),
  `Liabilities` = VALUES(`Liabilities`),
  `Total Shareholder Equity` = VALUES(`Total Shareholder Equity`),
  `Total Liabilities and Shareholder Equity` = VALUES(`Total Liabilities and Shareholder Equity`);"""
    
    return f"{table_definition}\n{all_values}\n{on_duplicate}"

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

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! from MCP sec-10ks"

if __name__ == "__main__":
    mcp.run()
