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
    debug_info = []
    
    try:
        # Clean the CIK input
        cleaned_cik = "".join(filter(str.isdigit, cik))
        debug_info.append(f"Processing {company_name} - CIK: {cleaned_cik}, FY: {year}")
        
        # Get the company and filing
        company = Company(cleaned_cik)
        
        # Get all filings for debugging with better error handling
        try:
            filings = company.get_filings(form="10-K")
            debug_info.append(f"Found {len(filings)} total 10-K filings")
            
            # Try to show first few filings for debugging
            try:
                for i, filing in enumerate(filings[:3]):
                    # Try different ways to access the filing data
                    try:
                        period = filing.period_of_report
                        filed = filing.filing_date
                        debug_info.append(f"  Filing {i+1}: period={period}, filed={filed}")
                    except Exception as attr_error:
                        debug_info.append(f"  Filing {i+1}: Error accessing attributes - {attr_error}")
                        # Try alternative access methods
                        try:
                            debug_info.append(f"  Filing {i+1}: Available attrs: {dir(filing)[:5]}")
                        except:
                            debug_info.append(f"  Filing {i+1}: Could not inspect filing")
            except Exception as list_error:
                debug_info.append(f"Error iterating filings: {list_error}")
            
        except Exception as e:
            debug_info.append(f"Error getting filings: {e}")
            return f"DEBUG: {'; '.join(debug_info)}"
        
        # Try to find a filing that represents the requested fiscal year data
        try:
            selected_filing = None
            
            for filing in filings:
                try:
                    # Get the filing date
                    filing_date = filing.filing_date if hasattr(filing, 'filing_date') else None
                    
                    if filing_date:
                        filing_str = str(filing_date)
                        debug_info.append(f"  Raw filing date: {filing_str}")
                        
                        # Handle different date formats
                        filing_year = None
                        filing_month = None
                        filing_day = None
                        
                        if len(filing_str) == 8 and filing_str.isdigit():
                            # Format: YYYYMMDD
                            filing_year = int(filing_str[:4])
                            filing_month = int(filing_str[4:6])
                            filing_day = int(filing_str[6:8])
                        elif '-' in filing_str:
                            # Format: YYYY-MM-DD or MM-DD-YYYY
                            parts = filing_str.split('-')
                            if len(parts) == 3:
                                if len(parts[0]) == 4:
                                    # YYYY-MM-DD
                                    filing_year = int(parts[0])
                                    filing_month = int(parts[1])
                                    filing_day = int(parts[2])
                                elif len(parts[2]) == 4:
                                    # MM-DD-YYYY
                                    filing_year = int(parts[2])
                                    filing_month = int(parts[0])
                                    filing_day = int(parts[1])
                        elif '/' in filing_str:
                            # Format: MM/DD/YYYY or YYYY/MM/DD
                            parts = filing_str.split('/')
                            if len(parts) == 3:
                                if len(parts[0]) == 4:
                                    # YYYY/MM/DD
                                    filing_year = int(parts[0])
                                    filing_month = int(parts[1])
                                    filing_day = int(parts[2])
                                elif len(parts[2]) == 4:
                                    # MM/DD/YYYY
                                    filing_year = int(parts[2])
                                    filing_month = int(parts[0])
                                    filing_day = int(parts[1])
                        
                        if filing_year and filing_month and filing_day:
                            # Calculate what data year this filing represents
                            if filing_month < 7 or (filing_month == 6 and filing_day <= 30):
                                data_year = filing_year - 1  # Filed by June 30 = previous year's data
                            else:
                                data_year = filing_year  # Filed after June 30 = same year's data
                            
                            debug_info.append(f"  Filing {filing_year}-{filing_month:02d}-{filing_day:02d} → data year {data_year}")
                            
                            if data_year == year:
                                selected_filing = filing
                                debug_info.append(f"✅ Selected filing {filing_year}-{filing_month:02d}-{filing_day:02d} for FY {year}")
                                break
                        else:
                            debug_info.append(f"  Could not parse date format: {filing_str}")
                    
                except Exception as filing_error:
                    debug_info.append(f"Error checking filing: {filing_error}")
                    continue
            
            if not selected_filing:
                debug_info.append(f"No filing found that represents FY {year} data")
                return f"DEBUG: {'; '.join(debug_info)}"
            
        except Exception as search_error:
            debug_info.append(f"Error searching filings: {search_error}")
            return f"DEBUG: {'; '.join(debug_info)}"
        
        # Try to get the full filing object
        try:
            full_filing = selected_filing.obj()
            debug_info.append("Got full filing object")
        except Exception as obj_error:
            debug_info.append(f"Error getting filing object: {obj_error}")
            return f"DEBUG: {'; '.join(debug_info)}"
        
        # Get income statement and balance sheet as markdown
        try:
            income_statement = full_filing.income_statement.to_dataframe()
            income_statement_markdown = income_statement.to_markdown()
            debug_info.append("Got income statement")
        except Exception as e:
            debug_info.append(f"Error getting income statement: {e}")
            return f"DEBUG: {'; '.join(debug_info)}"
        
        try:
            balance_sheet = full_filing.balance_sheet.to_dataframe()
            balance_sheet_markdown = balance_sheet.to_markdown()
            debug_info.append("Got balance sheet")
        except Exception as e:
            debug_info.append(f"Error getting balance sheet: {e}")
            return f"DEBUG: {'; '.join(debug_info)}"
        
        # Get the actual FILING date (when submitted to SEC)
        try:
            # Always try to get the filing_date first - this is when it was actually filed
            if hasattr(full_filing, 'filing_date') and full_filing.filing_date:
                report_date = full_filing.filing_date
                debug_info.append(f"Using filing_date: {report_date}")
            elif hasattr(selected_filing, 'filing_date') and selected_filing.filing_date:
                report_date = selected_filing.filing_date  
                debug_info.append(f"Using selected_filing.filing_date: {report_date}")
            else:
                # Fallback to period_of_report but this should be rare
                report_date = selected_filing.period_of_report
                debug_info.append(f"Fallback to period_of_report: {report_date}")
            
            # Format report date properly
            if isinstance(report_date, str):
                # Convert YYYYMMDD to YYYY-MM-DD
                if len(report_date) == 8:
                    formatted_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
                else:
                    formatted_date = report_date
            else:
                formatted_date = str(report_date)
            
            debug_info.append(f"Formatted report date: {formatted_date}")
            
            # Calculate the data year based on filing date
            filing_year = int(formatted_date[:4]) if len(formatted_date) >= 4 else year
            filing_month = int(formatted_date[5:7]) if len(formatted_date) >= 7 else 7
            filing_day = int(formatted_date[8:10]) if len(formatted_date) >= 10 else 1
            
            # Simple rule: If filed by June 30, data is from previous year
            if filing_month < 7 or (filing_month == 6 and filing_day <= 30):
                data_year = filing_year - 1
                debug_info.append(f"Filed by June 30 ({filing_month:02d}-{filing_day:02d}) → Data year: {data_year}")
            else:
                data_year = filing_year
                debug_info.append(f"Filed after June 30 ({filing_month:02d}-{filing_day:02d}) → Data year: {data_year}")
            
            # Check if this matches what we were looking for
            if data_year == year:
                debug_info.append(f"✅ Data year {data_year} matches requested FY {year}")
            else:
                debug_info.append(f"⚠️  Data year {data_year} != requested FY {year}")
                
        except Exception as e:
            debug_info.append(f"Error formatting date: {e}")
            formatted_date = f"{year+1}-03-31"  # fallback
            data_year = year
        
        # Create the extraction prompt for VALUES only
        extraction_prompt = _create_values_extraction_prompt(
            company_name, 
            year,  # Pass the fiscal year we want
            formatted_date,  # Pass the actual report date
            income_statement_markdown, 
            balance_sheet_markdown
        )
        
        # Use sampling to request LLM processing
        result = await ctx.sample(extraction_prompt)
        debug_info.append("LLM processing completed")
        
        # Extract just the VALUES clause from the result
        values_clause = _extract_values_clause(result.text)
        
        if values_clause and values_clause.strip():
            debug_info.append(f"SUCCESS")
            return values_clause
        else:
            debug_info.append("No VALUES clause extracted")
            return f"DEBUG: {'; '.join(debug_info)}"
        
    except Exception as e:
        debug_info.append(f"Exception: {e}")
        return f"DEBUG: {'; '.join(debug_info)}"

async def _get_10k_filing_for_fiscal_year_with_logging(company: Company, fiscal_year: int, ctx: Context):
    """
    Helper function to get the 10-K filing for a specific fiscal year with logging.
    
    Logic: If you want fiscal year 2023, look for:
    - A filing with period_of_report ending in 2023 (like 20231231)
    - That was filed in 2024 (the following year)
    """
    from datetime import datetime
    
    try:
        filings = company.get_filings(form="10-K")
        await ctx.info(f"Found {len(filings)} total 10-K filings for CIK {company.cik}")
        
        if not filings:
            await ctx.error(f"No 10-K filings found at all for CIK {company.cik}")
            return None
        
        for filing in filings:
            # period_of_report is a string in YYYYMMDD format
            period_str = filing.period_of_report
            await ctx.info(f"  Filing period: {period_str}, Filing date: {filing.filing_date}")
            
            if len(period_str) != 8:
                await ctx.info(f"    Skipping - invalid period format")
                continue
                
            try:
                # Parse the period end date (this is the fiscal year we care about)
                period_year = int(period_str[:4])
                
                await ctx.info(f"    Period year: {period_year}, Looking for FY: {fiscal_year}")
                
                # Simple logic: if the period year matches the fiscal year we want, use it
                if period_year == fiscal_year:
                    await ctx.info(f"    ✅ Found matching filing for FY {fiscal_year}")
                    return filing.obj()
                else:
                    await ctx.info(f"    ❌ Period year {period_year} != requested FY {fiscal_year}")
                    
            except ValueError as e:
                await ctx.info(f"    Skipping - date parse error: {e}")
                continue
        
        await ctx.error(f"No 10-K filing found with period ending in {fiscal_year}")
        return None
        
    except Exception as e:
        await ctx.error(f"Error getting filings for CIK {company.cik}: {e}")
        return None

def _get_10k_filing_for_fiscal_year(company: Company, fiscal_year: int):
    """
    Helper function to get the 10-K filing for a specific fiscal year.
    (Non-async version for backward compatibility)
    """
    from datetime import datetime
    
    filings = company.get_filings(form="10-K")
    
    for filing in filings:
        # period_of_report is a string in YYYYMMDD format
        period_str = filing.period_of_report
        if len(period_str) != 8:
            continue
            
        try:
            # Parse the date
            filing_date = datetime.strptime(period_str, "%Y%m%d")
            filing_year = filing_date.year
            filing_month = filing_date.month
            filing_day = filing_date.day
            
            # Check if this filing matches our fiscal year
            matches_fiscal_year = False
            
            if filing_year == fiscal_year + 1:
                # Next calendar year - check if it's June 30th or earlier
                if filing_month < 7 or (filing_month == 6 and filing_day <= 30):
                    matches_fiscal_year = True
            elif filing_year == fiscal_year:
                # Same calendar year - check if it's July 1st or later
                if filing_month > 7 or (filing_month == 7 and filing_day >= 1):
                    matches_fiscal_year = True
            
            if matches_fiscal_year:
                return filing.obj()  # .obj() gets the full filing object
                
        except ValueError:
            # Skip filings with invalid date formats
            continue
    
    return None

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
    Generate a bulk INSERT statement from list of VALUES clauses with ON DUPLICATE KEY UPDATE
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
  `Total Liabilities and Shareholder Equity` = VALUES(`Total Liabilities and Shareholder Equity`)"""
    
    return f"{table_definition}\n{all_values}\n{on_duplicate};"

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
        
        await ctx.info(f"Processing financial data for {company_name} ({cleaned_cik}) for fiscal year {year}")
        
        # Get the company and filing
        company = Company(cleaned_cik)
        filing = _get_10k_filing_for_fiscal_year(company, year)
        
        if not filing:
            return f"No 10-K filing found for CIK {cleaned_cik} for fiscal year {year}."
        
        # Get income statement and balance sheet as markdown
        await ctx.info("Downloading income statement...")
        income_statement = filing.income_statement.to_dataframe()
        income_statement_markdown = income_statement.to_markdown()
        
        await ctx.info("Downloading balance sheet...")
        balance_sheet = filing.balance_sheet.to_dataframe()
        balance_sheet_markdown = balance_sheet.to_markdown()
        
        # Get the actual report date from the filing
        report_date = filing.filing_date if hasattr(filing, 'filing_date') else filing.period_of_report
        
        # Format report date properly
        if isinstance(report_date, str):
            # Convert YYYYMMDD to YYYY-MM-DD
            if len(report_date) == 8:
                formatted_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
            else:
                formatted_date = report_date
        else:
            formatted_date = str(report_date)
        
        # Create the extraction prompt
        extraction_prompt = _create_extraction_prompt(
            company_name, 
            year,
            formatted_date,
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

def _create_values_extraction_prompt(company_name: str, fiscal_year: int, report_date: str, income_statement_markdown: str, balance_sheet_markdown: str) -> str:
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
- Negative shareholder equity is valid (means company owes more than it owns)
- Respond with ONLY the VALUES clause, no other text
"""

def _create_extraction_prompt(company_name: str, fiscal_year: int, report_date: str, income_statement_markdown: str, balance_sheet_markdown: str) -> str:
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

The company name should be "{company_name}".
The fiscal year should be {fiscal_year}.
The report date should be '{report_date}'.
"""

if __name__ == "__main__":
    mcp.run()