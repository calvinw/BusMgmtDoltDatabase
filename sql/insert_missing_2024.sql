-- INSERT missing 2024 data for American companies
-- All values converted to thousands to match database format

INSERT INTO financials (
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
VALUES
  ('Nike', 2024, '2025-05-31', 46309000, 26519000, 19790000, 16088000, 3702000, 3219000, 7489000, 23362000, 36579000, 10566000, 23366000, 13213000, 36579000)
ON DUPLICATE KEY UPDATE
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
  `Total Liabilities and Shareholder Equity` = VALUES(`Total Liabilities and Shareholder Equity`);