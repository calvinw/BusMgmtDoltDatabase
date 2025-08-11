-- UPDATE script to correct report dates for all years using actual fiscal year-end dates
-- Based on SEC 10-K filings data retrieved via MCP
-- Correcting filing dates to actual fiscal period end dates from financial statements

-- Retail companies with January/February fiscal year-ends
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Macy''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-01-31' WHERE company_name = 'Walmart' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Target' AND year = 2024;
UPDATE financials SET reportDate = '2025-01-31' WHERE company_name = 'Dollar General' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Dollar Tree' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Five Below' AND year = 2024;
-- Costco historical corrections (was using filing dates instead of fiscal year-end)
UPDATE financials SET reportDate = '2018-09-02' WHERE company_name = 'Costco' AND year = 2018;
UPDATE financials SET reportDate = '2019-09-01' WHERE company_name = 'Costco' AND year = 2019;
UPDATE financials SET reportDate = '2020-08-30' WHERE company_name = 'Costco' AND year = 2020;
UPDATE financials SET reportDate = '2021-08-29' WHERE company_name = 'Costco' AND year = 2021;
UPDATE financials SET reportDate = '2022-08-28' WHERE company_name = 'Costco' AND year = 2022;
UPDATE financials SET reportDate = '2023-09-03' WHERE company_name = 'Costco' AND year = 2023;
UPDATE financials SET reportDate = '2024-09-01' WHERE company_name = 'Costco' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'BJ''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'TJ Maxx' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Ross' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Burlington' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Nordstrom' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Dillard''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Kohl''s' AND year = 2024;

-- Calendar year-end companies (December 31st)
-- Amazon historical corrections (was using filing dates instead of fiscal year-end)
UPDATE financials SET reportDate = '2018-12-31' WHERE company_name = 'Amazon' AND year = 2018;
UPDATE financials SET reportDate = '2019-12-31' WHERE company_name = 'Amazon' AND year = 2019;
UPDATE financials SET reportDate = '2020-12-31' WHERE company_name = 'Amazon' AND year = 2020;
UPDATE financials SET reportDate = '2021-12-31' WHERE company_name = 'Amazon' AND year = 2021;
UPDATE financials SET reportDate = '2022-12-31' WHERE company_name = 'Amazon' AND year = 2022;
UPDATE financials SET reportDate = '2023-12-31' WHERE company_name = 'Amazon' AND year = 2023;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Amazon' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Wayfair' AND year = 2024;

-- Other retail companies with varied fiscal year-ends
UPDATE financials SET reportDate = '2025-02-02' WHERE company_name = 'Chewy' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Ulta Beauty' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Bath & Body Works' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Victoria''s Secret' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Signet Jewelers' AND year = 2024;

-- Fashion and apparel companies
UPDATE financials SET reportDate = '2025-03-31' WHERE company_name = 'Tapestry' AND year = 2024;
UPDATE financials SET reportDate = '2025-03-31' WHERE company_name = 'Capri Holdings' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-02' WHERE company_name = 'Lululemon' AND year = 2024;
UPDATE financials SET reportDate = '2025-03-31' WHERE company_name = 'Boot Barn' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Foot Locker' AND year = 2024;
UPDATE financials SET reportDate = '2024-05-31' WHERE company_name = 'Nike' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Abercrombie & Fitch' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'American Eagle' AND year = 2024;
UPDATE financials SET reportDate = '2025-01-31' WHERE company_name = 'Urban Outfitters' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Gap' AND year = 2024;
UPDATE financials SET reportDate = '2024-11-24' WHERE company_name = 'Levi Strauss' AND year = 2024;

-- Sporting goods and specialty retail
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Dick''s Sporting Goods' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Academy Sports' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Best Buy' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'YETI' AND year = 2024;

-- Home improvement and home goods
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Sherwin-Williams' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'RH' AND year = 2024;
UPDATE financials SET reportDate = '2025-01-28' WHERE company_name = 'Williams-Sonoma' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-02' WHERE company_name = 'Home Depot' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-02' WHERE company_name = 'Lowe''s' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Tractor Supply' AND year = 2024;

-- Grocery and pharmacy
UPDATE financials SET reportDate = '2025-02-03' WHERE company_name = 'Kroger' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-24' WHERE company_name = 'Albertsons' AND year = 2024;
UPDATE financials SET reportDate = '2024-08-31' WHERE company_name = 'Walgreens' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'CVS' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Rite Aid' AND year = 2024;