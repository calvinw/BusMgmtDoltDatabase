# BusMgmtBenchmarks REST API Documentation

This document provides comprehensive examples of using the DoltHub REST API to access the `calvinw/BusMgmtBenchmarks` database. The API returns data in JSON format and is perfect for building web applications that need financial benchmarking data.

## Base URL Structure

All API calls follow this pattern:
```
https://www.dolthub.com/api/v1alpha1/{owner}/{database}
```

For the BusMgmtBenchmarks database:
```
https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
```

## Authentication

The BusMgmtBenchmarks database is public, so no authentication is required for read operations.

## Basic Database Metadata

Get basic information about the database:

```http
GET https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
```

**Response:**
```json
{
  "owner": "calvinw",
  "repo_name": "BusMgmtBenchmarks",
  "description": "Business Management Benchmarks database",
  "branch": "main"
}
```

## Table Listing

Get all tables in the database:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SHOW TABLES"
}
```

**Response:**
```json
{
  "query_execution_status": "Success",
  "query_execution_message": "",
  "schema": [
    {
      "columnName": "Tables_in_BusMgmtBenchmarks",
      "columnType": "TEXT"
    }
  ],
  "rows": [
    ["financials"],
    ["new_company_info"],
    ["new_financial_metrics"],
    ["segment_metrics"],
    ["subsegment_metrics"]
  ]
}
```

## Core Table Queries

### 1. Company Information

Get all companies with their segments and subsegments:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company, display_name, ticker_symbol, segment, subsegment FROM new_company_info ORDER BY segment, display_name"
}
```

Find companies in a specific segment:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM new_company_info WHERE segment = 'Technology' ORDER BY display_name"
}
```

### 2. Financial Data

Get financial data for a specific company and year:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM financials WHERE company_name = 'Apple Inc.' AND year = 2023"
}
```

Get revenue data for all companies in a specific year:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company_name, year, `Net Revenue`, `Gross Margin`, `Operating Profit`, `Net Profit` FROM financials WHERE year = 2023 ORDER BY `Net Revenue` DESC"
}
```

### 3. Financial Metrics

Get financial ratios for a specific company:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM new_financial_metrics WHERE company_name = 'Apple Inc.' AND year = 2023"
}
```

Get profitability metrics for all companies in a year:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company_name, year, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM new_financial_metrics WHERE year = 2023 ORDER BY Return_on_Assets DESC"
}
```

## Benchmark Queries

### 1. Segment Benchmarks

Get benchmark metrics for all segments in a specific year:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM segment_metrics WHERE year = 2023 ORDER BY segment"
}
```

Get specific segment benchmark:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT segment, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM segment_metrics WHERE segment = 'Technology' AND year = 2023"
}
```

### 2. Subsegment Benchmarks

Get subsegment benchmarks for a specific year:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM subsegment_metrics WHERE year = 2023 ORDER BY subsegment"
}
```

## Using Pre-built Views

### 1. Company Benchmarks View

Get comprehensive company data using the benchmarks view:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT * FROM `benchmarks 2023 view` WHERE company = 'Apple Inc.'"
}
```

Get all companies in a segment with their metrics:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company, segment, `Net Revenue`, `Gross Margin %`, `Operating Profit Margin %`, `Net Profit Margin %`, `Return on Assets` FROM `benchmarks 2023 view` WHERE segment = 'Technology' ORDER BY `Net Revenue` DESC"
}
```

### 2. Segment and Company Comparison

Compare a company to its segment benchmark:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT segment, company, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM `segment and company benchmarks 2023` WHERE segment = 'Technology' OR company = 'Apple Inc.' ORDER BY segment DESC, company"
}
```

## Advanced Analytics Queries

### 1. Multi-Year Trend Analysis

Get revenue growth trends for a company:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company_name, year, `Net Revenue`, Sales_Current_Year_vs_LY, Three_Year_Revenue_CAGR FROM new_financial_metrics WHERE company_name = 'Apple Inc.' AND year >= 2020 ORDER BY year"
}
```

### 2. Peer Comparison

Compare multiple companies within the same segment:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT c.display_name, c.segment, m.Gross_Margin_Percentage, m.Operating_Profit_Margin_Percentage, m.Return_on_Assets FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE c.segment = 'Technology' AND m.year = 2023 ORDER BY m.Return_on_Assets DESC"
}
```

### 3. Top Performers Analysis

Find top performing companies by Return on Assets:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT c.display_name, c.segment, m.Return_on_Assets, m.Net_Profit_Margin_Percentage, m.Asset_Turnover FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE m.year = 2023 AND m.Return_on_Assets IS NOT NULL ORDER BY m.Return_on_Assets DESC LIMIT 10"
}
```

### 4. Segment Performance Rankings

Rank segments by average profitability:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT segment, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM segment_metrics WHERE year = 2023 ORDER BY Return_on_Assets DESC"
}
```

## Financial Health Analysis

### 1. Liquidity Analysis

Get liquidity ratios for companies:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT c.display_name, c.segment, m.Current_Ratio, m.Quick_Ratio, m.Debt_to_Equity FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE m.year = 2023 AND m.Current_Ratio IS NOT NULL ORDER BY m.Current_Ratio DESC"
}
```

### 2. Efficiency Metrics

Analyze operational efficiency:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT c.display_name, c.segment, m.Asset_Turnover, m.Inventory_Turnover, m.SGA_Percentage FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE m.year = 2023 AND c.segment = 'Retail' ORDER BY m.Asset_Turnover DESC"
}
```

## URL Encoding for Complex Queries

For complex queries with special characters, ensure proper URL encoding. Here's an example using a URL-encoded query:

```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company, segment, `Net Revenue`, `Gross Margin %` FROM `benchmarks 2023 view` WHERE `Net Revenue` > 1000000 ORDER BY `Net Revenue` DESC"
}
```

## Response Format

All successful queries return JSON in this format:

```json
{
  "query_execution_status": "Success",
  "query_execution_message": "",
  "schema": [
    {
      "columnName": "column_name",
      "columnType": "DATA_TYPE"
    }
  ],
  "rows": [
    ["value1", "value2", "value3"],
    ["value4", "value5", "value6"]
  ]
}
```

## Error Handling

If a query fails, you'll receive an error response:

```json
{
  "query_execution_status": "Error",
  "query_execution_message": "Error message describing what went wrong",
  "schema": null,
  "rows": null
}
```

## Best Practices for Web Applications

1. **Pagination**: For large result sets, use `LIMIT` and `OFFSET` clauses
2. **Filtering**: Always use `WHERE` clauses to limit data retrieval
3. **Indexing**: The database is optimized for queries on company_name, year, segment, and subsegment
4. **Caching**: Consider caching benchmark data as it doesn't change frequently
5. **Error Handling**: Always check the `query_execution_status` field before processing results

## Common Use Cases for Web Applications

### Dashboard Widgets

**Company Performance Summary:**
```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT company, `Net Revenue`, `Gross Margin %`, `Operating Profit Margin %`, `Return on Assets` FROM `benchmarks 2023 view` WHERE company = 'Apple Inc.'"
}
```

**Segment Comparison Chart:**
```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT segment, AVG(Operating_Profit_Margin_Percentage) as avg_op_margin FROM segment_metrics WHERE year = 2023 GROUP BY segment ORDER BY avg_op_margin DESC"
}
```

### Search and Filter APIs

**Company Search:**
```http
POST https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks
Content-Type: application/json

{
  "query": "SELECT display_name, ticker_symbol, segment FROM new_company_info WHERE display_name LIKE '%Apple%' OR ticker_symbol LIKE '%AAPL%'"
}
```

This REST API provides powerful access to comprehensive financial benchmarking data that can power sophisticated business intelligence applications, dashboards, and analytical tools.
