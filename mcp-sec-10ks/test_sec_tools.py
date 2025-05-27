from mcp_sec_10ks import get_10k_income_statement, get_10k_balance_sheet, set_identity

if __name__ == "__main__":
    # Set identity for edgartools
    set_identity("Calvin Williamson calvin_williamson@fitnyc.edu")

    cik = "1397187"  # Lululemon CIK
    year = 2024

    print(f"Fetching income statement for CIK: {cik}, Year: {year}")
    income_statement_markdown = get_10k_income_statement(year, cik)
    print("\nIncome Statement:")
    print(income_statement_markdown)

    print(f"\nFetching balance sheet for CIK: {cik}, Year: {year}")
    balance_sheet_markdown = get_10k_balance_sheet(year, cik)
    print("\nBalance Sheet:")
    print(balance_sheet_markdown)
