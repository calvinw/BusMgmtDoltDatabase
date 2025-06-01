Here is an overview of the `calvinw/BusMgmtBenchmarks/main` database:

## Database Schema Overview

This database contains financial and company information, along with calculated financial metrics and benchmark data at the segment and subsegment levels.

Here are the tables in the database:

*   `financials`: Contains raw financial data for companies.
*   `new_company_info`: Provides company-specific information, including segment and subsegment classifications.
*   `new_financial_metrics`: Stores calculated financial ratios and metrics for each company and year.
*   `segment_metrics`: Holds benchmark financial metrics aggregated at the segment level for each year.
*   `subsegment_metrics`: Holds benchmark financial metrics aggregated at the subsegment level for each year.

### Table Descriptions

**`financials`**

| Field                                    | Type         | Null | Key | Default | Extra |
| ---------------------------------------- | ------------ | ---- | --- | ------- | ----- |
| company_name                             | varchar(255) | NO   | PRI | NULL    |       |
| year                                     | int          | NO   | PRI | NULL    |       |
| reportDate                               | date         | NO   |     | NULL    |       |
| Net Revenue                              | bigint       | YES  |     | NULL    |       |
| Cost of Goods                            | bigint       | YES  |     | NULL    |       |
| Gross Margin                             | bigint       | YES  |     | NULL    |       |
| SGA                                      | bigint       | YES  |     | NULL    |       |
| Operating Profit                         | bigint       | YES  |     | NULL    |       |
| Net Profit                               | bigint       | YES  |     | NULL    |       |
| Inventory                                | bigint       | YES  |     | NULL    |       |
| Current Assets                           | bigint       | YES  |     | NULL    |       |
| Total Assets                             | bigint       | YES  |     | NULL    |       |
| Current Liabilities                      | bigint       | YES  |     | NULL    |       |
| Liabilities                              | bigint       | YES  |     | NULL    |       |
| Total Shareholder Equity                 | bigint       | YES  |     | NULL    |       |
| Total Liabilities and Shareholder Equity | bigint       | YES  |     | NULL    |       |

**`new_company_info`**

| Field         | Type         | Null | Key | Default | Extra |
| ------------- | ------------ | ---- | --- | ------- | ----- |
| company       | varchar(255) | NO   | PRI | NULL    |       |
| CIK           | int          | YES  |     | NULL    |       |
| display_name  | varchar(255) | NO   |     | NULL    |       |
| ticker_symbol | varchar(10)  | NO   |     | NULL    |       |
| segment       | varchar(255) | YES  |     | NULL    |       |
| subsegment    | varchar(255) | YES  |     | NULL    |       |
| currency      | varchar(10)  | YES  |     | NULL    |       |
| units         | varchar(50)  | YES  |     | NULL    |       |

**`new_financial_metrics`**

| Field                              | Type          | Null | Key | Default | Extra |
| ---------------------------------- | ------------- | ---- | --- | ------- | ----- |
| company_name                       | varchar(255)  | NO   | PRI | NULL    |       |
| year                               | int           | NO   | PRI | NULL    |       |
| Cost_of_Goods_Percentage           | decimal(10,4) | YES  |     | NULL    |       |
| SGA_Percentage                     | decimal(10,4) | YES  |     | NULL    |       |
| Gross_Margin_Percentage            | decimal(10,4) | YES  |     | NULL    |       |
| Operating_Profit_Margin_Percentage | decimal(10,4) | YES  |     | NULL    |       |
| Net_Profit_Margin_Percentage       | decimal(10,4) | YES  |     | NULL    |       |
| Inventory_Turnover                 | decimal(10,4) | YES  |     | NULL    |       |
| Asset_Turnover                     | decimal(10,4) | YES  |     | NULL    |       |
| Return_on_Assets                   | decimal(10,4) | YES  |     | NULL    |       |
| Three_Year_Revenue_CAGR            | decimal(10,4) | YES  |     | NULL    |       |
| Sales_Current_Year_vs_LY           | decimal(10,4) | YES  |     | NULL    |       |
| Current_Ratio                      | decimal(10,4) | YES  |     | NULL    |       |
| Quick_Ratio                        | decimal(10,4) | YES  |     | NULL    |       |
| Debt_to_Equity                     | decimal(10,4) | YES  |     | NULL    |       |

**`segment_metrics`**

| Field                              | Type          | Null | Key | Default | Extra |
| ---------------------------------- | ------------- | ---- | --- | ------- | ----- |
| segment                            | varchar(255)  | NO   | PRI | NULL    |       |
| year                               | int           | NO   | PRI | 2024    |       |
| Cost_of_Goods_Percentage           | decimal(10,4) | YES  |     | NULL    |       |
| SGA_Percentage                     | decimal(10,4) | YES  |     | NULL    |       |
| Gross_Margin_Percentage            | decimal(10,4) | YES  |     | NULL    |       |
| Operating_Profit_Margin_Percentage | decimal(10,4) | YES  |     | NULL    |       |
| Net_Profit_Margin_Percentage       | decimal(10,4) | YES  |     | NULL    |       |
| Inventory_Turnover                 | decimal(10,4) | YES  |     | NULL    |       |
| Asset_Turnover                     | decimal(10,4) | YES  |     | NULL    |       |
| Return_on_Assets                   | decimal(10,4) | YES  |     | NULL    |       |
| Three_Year_Revenue_CAGR            | decimal(10,4) | YES  |     | NULL    |       |
| Sales_Current_Year_vs_LY           | decimal(10,4) | YES  |     | NULL    |       |
| Current_Ratio                      | decimal(10,4) | YES  |     | NULL    |       |
| Quick_Ratio                        | decimal(10,4) | YES  |     | NULL    |       |
| Debt_to_Equity                     | decimal(10,4) | YES  |     | NULL    |       |

**`subsegment_metrics`**

| Field                              | Type          | Null | Key | Default | Extra |
| ---------------------------------- | ------------- | ---- | --- | ------- | ----- |
| subsegment                         | varchar(255)  | NO   | PRI | NULL    |       |
| year                               | int           | NO   | PRI | 2024    |       |
| Cost_of_Goods_Percentage           | decimal(10,4) | YES  |     | NULL    |       |
| SGA_Percentage                     | decimal(10,4) | YES  |     | NULL    |       |
| Gross_Margin_Percentage            | decimal(10,4) | YES  |     | NULL    |       |
| Operating_Profit_Margin_Percentage | decimal(10,4) | YES  |     | NULL    |       |
| Net_Profit_Margin_Percentage       | decimal(10,4) | YES  |     | NULL    |       |
| Inventory_Turnover                 | decimal(10,4) | YES  |     | NULL    |       |
| Asset_Turnover                     | decimal(10,4) | YES  |     | NULL    |       |
| Return_on_Assets                   | decimal(10,4) | YES  |     | NULL    |       |
| Three_Year_Revenue_CAGR            | decimal(10,4) | YES  |     | NULL    |       |
| Sales_Current_Year_vs_LY           | decimal(10,4) | YES  |     | NULL    |       |
| Current_Ratio                      | decimal(10,4) | YES  |     | NULL    |       |
| Quick_Ratio                        | decimal(10,4) | YES  |     | NULL    |       |
| Debt_to_Equity                     | decimal(10,4) | YES  |     | NULL    |       |

## Views Overview

The database contains several views, primarily focused on providing benchmark data at different levels (company, segment, and subsegment) for various years.

Here are the views and their descriptions:

*   **`benchmarks [year] view` (e.g., `benchmarks 2018 view`, `benchmarks 2019 view`, etc.):** These views combine financial data from the `financials` table with company information from `new_company_info` and calculated financial metrics from `new_financial_metrics` for a specific year. They provide a comprehensive view of a company's financial performance and key ratios, including year-over-year revenue comparisons where applicable.

    ```sql
    CREATE VIEW `benchmarks 2018 view` AS 
    SELECT 
        subquery.company_name AS company,
        subquery.year AS year,
        subquery.reportDate,
        subquery.segment,
        subquery.subsegment,
        subquery.`Net Revenue`,
        subquery.`Cost of Goods`,
        subquery.`Gross Margin`,
        subquery.`SGA`,
        subquery.`Operating Profit`,
        subquery.`Net Profit`,
        subquery.`Inventory`,
        subquery.`Current Assets`,
        subquery.`Total Assets`,
        subquery.`Current Liabilities`,
        subquery.`Total Shareholder Equity`,
        subquery.`Total Liabilities and Shareholder Equity`,
        fm.`Cost_of_Goods_Percentage` AS `Cost of Goods %`,
        fm.`SGA_Percentage` AS `SGA %`,
        fm.`Gross_Margin_Percentage` AS `Gross Margin %`,
        fm.`Operating_Profit_Margin_Percentage` AS `Operating Profit Margin %`,
        fm.`Net_Profit_Margin_Percentage` AS `Net Profit Margin %`,
        fm.`Inventory_Turnover` AS `Inventory Turnover`,
        fm.`Asset_Turnover` AS `Asset Turnover`,
        fm.`Return_on_Assets` AS `Return on Assets`,
        fm.`Three_Year_Revenue_CAGR` AS `Three Year Revenue CAGR`,
        fm.`Sales_Current_Year_vs_LY` AS `Sales vs LY`,
        fm.`Current_Ratio` AS `Current Ratio`,
        fm.`Quick_Ratio` AS `Quick Ratio`,
        fm.`Debt_to_Equity` AS `Debt to Equity`
    FROM (
        SELECT 
            f.*,
            c.segment,
            c.subsegment
        FROM 
            financials f
        JOIN 
            new_company_info c ON f.company_name = c.company
        WHERE 
            f.year = 2018
    ) AS subquery
    JOIN 
        new_financial_metrics fm ON subquery.company_name = fm.company_name AND subquery.year = fm.year
    ```
    *(Note: The view definitions for other years are similar, including additional columns for Net Revenue from previous years for CAGR calculations.)*

*   **`segment and company benchmarks [year]` (e.g., `segment and company benchmarks 2018`, `segment and company benchmarks 2019`, etc.):** These views combine segment-level benchmark metrics from `segment_metrics` and company-level financial metrics from `new_financial_metrics` for a specific year. They allow for easy comparison of individual company performance against their respective segment benchmarks.

    ```sql
    CREATE VIEW `segment and company benchmarks 2018` AS 
    SELECT 
        CASE 
            WHEN type = 'Segment' THEN name 
            ELSE '' 
        END AS segment,
        CASE 
            WHEN type = 'Company' THEN name 
            ELSE '' 
        END AS company,
        Cost_of_Goods_Percentage AS Cost_of_Goods_Percentage,
        SGA_Percentage AS SGA_Percentage,
        Gross_Margin_Percentage AS Gross_Margin_Percentage,
        Operating_Profit_Margin_Percentage AS Operating_Profit_Margin_Percentage,
        Net_Profit_Margin_Percentage AS Net_Profit_Margin_Percentage,
        Inventory_Turnover AS Inventory_Turnover,
        Asset_Turnover AS Asset_Turnover,
        Return_on_Assets AS Return_on_Assets,
        Three_Year_Revenue_CAGR AS Three_Year_Revenue_CAGR,
        Sales_Current_Year_vs_LY AS Sales_Current_Year_vs_LY,
        Current_Ratio AS Current_Ratio,
        Quick_Ratio AS Quick_Ratio,
        Debt_to_Equity AS Debt_to_Equity
    FROM (
        SELECT 
            sm.segment AS name,
            sm.Cost_of_Goods_Percentage,
            sm.SGA_Percentage,
            sm.Gross_Margin_Percentage,
            sm.Operating_Profit_Margin_Percentage,
            sm.Net_Profit_Margin_Percentage,
            sm.Inventory_Turnover,
            sm.Asset_Turnover,
            sm.Return_on_Assets,
            sm.Three_Year_Revenue_CAGR,
            sm.Current_Ratio,
            sm.Quick_Ratio,
            sm.Sales_Current_Year_vs_LY,
            sm.Debt_to_Equity,
            'Segment' AS type,
            sm.segment AS segment_name
        FROM 
            segment_metrics sm
        WHERE 
            sm.year = 2018

        UNION ALL

        SELECT 
            ci.display_name AS name,
            nfm.Cost_of_Goods_Percentage,
            nfm.SGA_Percentage,
            nfm.Gross_Margin_Percentage,
            nfm.Operating_Profit_Margin_Percentage,
            nfm.Net_Profit_Margin_Percentage,
            nfm.Inventory_Turnover,
            nfm.Asset_Turnover,
            nfm.Return_on_Assets,
            nfm.Three_Year_Revenue_CAGR,
            nfm.Current_Ratio,
            nfm.Quick_Ratio,
            nfm.Sales_Current_Year_vs_LY,
            nfm.Debt_to_Equity,
            'Company' AS type,
            ci.segment AS segment_name
        FROM 
            new_financial_metrics nfm
        JOIN 
            new_company_info ci ON nfm.company_name = ci.company
        WHERE 
            nfm.year = 2018
    ) AS combined_data
    ORDER BY 
        segment_name, type DESC, name
    ```
    *(Note: The view definitions for other years are similar.)*

*   **`segment benchmarks [year]` (e.g., `segment benchmarks 2018`, `segment benchmarks 2019`, etc.):** These views provide the segment-level benchmark financial metrics from the `segment_metrics` table for a specific year.

    ```sql
    CREATE VIEW `segment benchmarks 2018` AS 
    SELECT 
        segment,
        year,
        Cost_of_Goods_Percentage AS Cost_of_Goods_Percentage,
        SGA_Percentage AS SGA_Percentage,
        Gross_Margin_Percentage AS Gross_Margin_Percentage,
        Operating_Profit_Margin_Percentage AS Operating_Profit_Margin_Percentage,
        Net_Profit_Margin_Percentage AS Net_Profit_Margin_Percentage,
        Inventory_Turnover AS Inventory_Turnover,
        Asset_Turnover AS Asset_Turnover,
        Return_on_Assets AS Return_on_Assets,
        Three_Year_Revenue_CAGR AS Three_Year_Revenue_CAGR,
        Sales_Current_Year_vs_LY AS Sales_Current_Year_vs_LY,
        Current_Ratio AS Current_Ratio,
        Quick_Ratio AS Quick_Ratio,
        Debt_to_Equity AS Debt_to_Equity
    FROM 
        segment_metrics 
    WHERE 
        year = 2018
    ```
    *(Note: The view definitions for other years are similar.)*

*   **`subsegment benchmarks [year]` (e.g., `subsegment benchmarks 2018`, `subsegment benchmarks 2019`, etc.):** These views provide the subsegment-level benchmark financial metrics from the `subsegment_metrics` table for a specific year.

    ```sql
    CREATE VIEW `subsegment benchmarks 2018` AS 
    SELECT 
        subsegment,
        year,
        Cost_of_Goods_Percentage AS Cost_of_Goods_Percentage,
        SGA_Percentage AS SGA_Percentage,
        Gross_Margin_Percentage AS Gross_Margin_Percentage,
        Operating_Profit_Margin_Percentage AS Operating_Profit_Margin_Percentage,
        Net_Profit_Margin_Percentage AS Net_Profit_Margin_Percentage,
        Inventory_Turnover AS Inventory_Turnover,
        Asset_Turnover AS Asset_Turnover,
        Return_on_Assets AS Return_on_Assets,
        Three_Year_Revenue_CAGR AS Three_Year_Revenue_CAGR,
        Sales_Current_Year_vs_LY AS Sales_Current_Year_vs_LY,
        Current_Ratio AS Current_Ratio,
        Quick_Ratio AS Quick_Ratio,
        Debt_to_Equity AS Debt_to_Equity
    FROM 
        subsegment_metrics 
    WHERE 
        year = 2018
    ```
    *(Note: The view definitions for other years are similar.)*

## Sample Queries

Here are a few sample queries to demonstrate how to retrieve data from this database:

*   **Get financial data for a specific company and year:**

    ```sql
    SELECT *
    FROM financials
    WHERE company_name = 'Your Company Name' AND year = 2023;
    ```

*   **Get financial metrics for a specific company and year:**

    ```sql
    SELECT *
    FROM new_financial_metrics
    WHERE company_name = 'Your Company Name' AND year = 2023;
    ```

*   **Get segment benchmarks for a specific segment and year:**

    ```sql
    SELECT *
    FROM `segment benchmarks 2023`
    WHERE segment = 'Your Segment Name';
    ```

*   **Compare a company's metrics to its segment benchmarks for a specific year:**

    ```sql
    SELECT *
    FROM `segment and company benchmarks 2023`
    WHERE segment = 'Your Segment Name' OR company = 'Your Company Display Name';
    ```

*   **Get all data from a specific year's benchmark view:**

    ```sql
    SELECT *
    FROM `benchmarks 2023 view`;
    ```


