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
  ('Amazon', 2024, '2025-02-07', 637959000.0, 326288000.0, 311671000.0, 55266000.0, 68593000.0, 59248000.0, 34214000.0, 190867000.0, 624894000.0, 179431000.0, 338924000.0, 285970000.0, 624894000.0),
  ('Costco', 2024, '2024-10-09', 254453000.0, 222358000.0, 32095000.0, 22810000.0, 9285000.0, 7367000.0, 18647000.0, 34246000.0, 69831000.0, 35464000.0, 46209000.0, 23622000.0, 69831000.0)
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
