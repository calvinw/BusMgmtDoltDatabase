-- Drop old year-specific views
DROP VIEW IF EXISTS `benchmarks 2018 view`;
DROP VIEW IF EXISTS `benchmarks 2019 view`;
DROP VIEW IF EXISTS `benchmarks 2020 view`;
DROP VIEW IF EXISTS `benchmarks 2021 view`;
DROP VIEW IF EXISTS `benchmarks 2022 view`;
DROP VIEW IF EXISTS `benchmarks 2023 view`;
DROP VIEW IF EXISTS `benchmarks 2024 view`;

DROP VIEW IF EXISTS `segment and company benchmarks 2018`;
DROP VIEW IF EXISTS `segment and company benchmarks 2019`;
DROP VIEW IF EXISTS `segment and company benchmarks 2020`;
DROP VIEW IF EXISTS `segment and company benchmarks 2021`;
DROP VIEW IF EXISTS `segment and company benchmarks 2022`;
DROP VIEW IF EXISTS `segment and company benchmarks 2023`;
DROP VIEW IF EXISTS `segment and company benchmarks 2024`;

DROP VIEW IF EXISTS `segment benchmarks 2018`;
DROP VIEW IF EXISTS `segment benchmarks 2019`;
DROP VIEW IF EXISTS `segment benchmarks 2020`;
DROP VIEW IF EXISTS `segment benchmarks 2021`;
DROP VIEW IF EXISTS `segment benchmarks 2022`;
DROP VIEW IF EXISTS `segment benchmarks 2023`;
DROP VIEW IF EXISTS `segment benchmarks 2024`;

DROP VIEW IF EXISTS `subsegment benchmarks 2018`;
DROP VIEW IF EXISTS `subsegment benchmarks 2019`;
DROP VIEW IF EXISTS `subsegment benchmarks 2020`;
DROP VIEW IF EXISTS `subsegment benchmarks 2021`;
DROP VIEW IF EXISTS `subsegment benchmarks 2022`;
DROP VIEW IF EXISTS `subsegment benchmarks 2023`;
DROP VIEW IF EXISTS `subsegment benchmarks 2024`;


-- Consolidated views

-- 1. Consolidated segment_benchmarks_all_years view
DROP VIEW IF EXISTS `segment_benchmarks_all_years`;
CREATE VIEW `segment_benchmarks_all_years` AS
SELECT
    segment,
    year,
    Cost_of_Goods_Percentage,
    SGA_Percentage,
    Gross_Margin_Percentage,
    Operating_Profit_Margin_Percentage,
    Net_Profit_Margin_Percentage,
    Inventory_Turnover,
    Asset_Turnover,
    Return_on_Assets,
    Three_Year_Revenue_CAGR,
    Sales_Current_Year_vs_LY,
    Current_Ratio,
    Quick_Ratio,
    Debt_to_Equity
FROM
    segment_metrics;

-- 2. Consolidated subsegment_benchmarks_all_years view
DROP VIEW IF EXISTS `subsegment_benchmarks_all_years`;
CREATE VIEW `subsegment_benchmarks_all_years` AS
SELECT
    subsegment,
    year,
    Cost_of_Goods_Percentage,
    SGA_Percentage,
    Gross_Margin_Percentage,
    Operating_Profit_Margin_Percentage,
    Net_Profit_Margin_Percentage,
    Inventory_Turnover,
    Asset_Turnover,
    Return_on_Assets,
    Three_Year_Revenue_CAGR,
    Sales_Current_Year_vs_LY,
    Current_Ratio,
    Quick_Ratio,
    Debt_to_Equity
FROM
    subsegment_metrics;

-- 3. Consolidated segment_and_company_benchmarks_all_years view
DROP VIEW IF EXISTS `segment_and_company_benchmarks_all_years`;
CREATE VIEW `segment_and_company_benchmarks_all_years` AS
SELECT
    CASE
        WHEN type = 'Segment' THEN name
        ELSE ''
    END AS segment,
    CASE
        WHEN type = 'Company' THEN name
        ELSE ''
    END AS company,
    year,
    Cost_of_Goods_Percentage,
    SGA_Percentage,
    Gross_Margin_Percentage,
    Operating_Profit_Margin_Percentage,
    Net_Profit_Margin_Percentage,
    Inventory_Turnover,
    Asset_Turnover,
    Return_on_Assets,
    Three_Year_Revenue_CAGR,
    Sales_Current_Year_vs_LY,
    Current_Ratio,
    Quick_Ratio,
    Debt_to_Equity
FROM (
    SELECT
        sm.segment AS name,
        sm.year,
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

    UNION ALL

    SELECT
        ci.display_name AS name,
        nfm.year,
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
        financial_metrics nfm
    JOIN
        company_info ci ON nfm.company_name = ci.company
) AS combined_data
ORDER BY
    segment_name, type DESC, name;

-- 4. Consolidated benchmarks_all_years view
DROP VIEW IF EXISTS `benchmarks_all_years`;
CREATE VIEW `benchmarks_all_years` AS
SELECT
    f.company_name AS company,
    f.year AS year,
    f.reportDate,
    ci.segment,
    ci.subsegment,
    f.`Net Revenue`,
    LAG(f.`Net Revenue`, 1) OVER (PARTITION BY f.company_name ORDER BY f.year) AS `Net Revenue Prev Year`,
    LAG(f.`Net Revenue`, 2) OVER (PARTITION BY f.company_name ORDER BY f.year) AS `Net Revenue Prev 2 Years`,
    LAG(f.`Net Revenue`, 3) OVER (PARTITION BY f.company_name ORDER BY f.year) AS `Net Revenue Prev 3 Years`,
    f.`Cost of Goods`,
    f.`Gross Margin`,
    f.`SGA`,
    f.`Operating Profit`,
    f.`Net Profit`,
    f.`Inventory`,
    f.`Current Assets`,
    f.`Total Assets`,
    f.`Current Liabilities`,
    f.`Total Shareholder Equity`,
    f.`Total Liabilities and Shareholder Equity`,
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
FROM
    financials f
JOIN
    company_info ci ON f.company_name = ci.company
JOIN
    financial_metrics fm ON f.company_name = fm.company_name AND f.year = fm.year;
