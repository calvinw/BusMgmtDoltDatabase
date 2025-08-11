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

...


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
