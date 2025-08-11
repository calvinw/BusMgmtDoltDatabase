-- UPDATE script to correct report dates only for 2024 data
-- Correcting fiscal year end dates to actual period end dates from SEC filings
-- Financial data remains unchanged - only reportDate field is updated

-- Major corrections: Filing dates → Actual fiscal year end dates
UPDATE financials SET reportDate = '2025-01-31' WHERE company_name = 'Walmart' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Target' AND year = 2024;
UPDATE financials SET reportDate = '2025-01-31' WHERE company_name = 'Dollar General' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Dollar Tree' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Five Below' AND year = 2024;
UPDATE financials SET reportDate = '2024-09-01' WHERE company_name = 'Costco' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'BJ''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'TJ Maxx' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Ross' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Burlington' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Macy''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Nordstrom' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Dillard''s' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Kohl''s' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Amazon' AND year = 2024;
UPDATE financials SET reportDate = '2024-12-31' WHERE company_name = 'Wayfair' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-02' WHERE company_name = 'Chewy' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Ulta Beauty' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Victoria''s Secret' AND year = 2024;
UPDATE financials SET reportDate = '2025-02-01' WHERE company_name = 'Signet Jewelers' AND year = 2024;