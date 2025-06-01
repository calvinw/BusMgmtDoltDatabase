-- Execute benchmark views
SELECT * FROM `benchmarks 2018 view`;
SELECT * FROM `benchmarks 2019 view`;
SELECT * FROM `benchmarks 2020 view`;
SELECT * FROM `benchmarks 2021 view`;
SELECT * FROM `benchmarks 2022 view`;
SELECT * FROM `benchmarks 2023 view`;
SELECT * FROM `benchmarks 2024 view`;

-- Execute segment and company benchmark views
SELECT * FROM `segment and company benchmarks 2018`;
SELECT * FROM `segment and company benchmarks 2019`;
SELECT * FROM `segment and company benchmarks 2020`;
SELECT * FROM `segment and company benchmarks 2021`;
SELECT * FROM `segment and company benchmarks 2022`;
SELECT * FROM `segment and company benchmarks 2023`;
SELECT * FROM `segment and company benchmarks 2024`;

-- Execute segment benchmark views
SELECT * FROM `segment benchmarks 2018`;
SELECT * FROM `segment benchmarks 2019`;
SELECT * FROM `segment benchmarks 2020`;
SELECT * FROM `segment benchmarks 2021`;
SELECT * FROM `segment benchmarks 2022`;
SELECT * FROM `segment benchmarks 2023`;
SELECT * FROM `segment benchmarks 2024`;

-- Execute subsegment benchmark views
SELECT * FROM `subsegment benchmarks 2018`;
SELECT * FROM `subsegment benchmarks 2019`;
SELECT * FROM `subsegment benchmarks 2020`;
SELECT * FROM `subsegment benchmarks 2021`;
SELECT * FROM `subsegment benchmarks 2022`;
SELECT * FROM `subsegment benchmarks 2023`;
SELECT * FROM `subsegment benchmarks 2024`;

-- Optional: Add LIMIT if you just want to see sample data
-- SELECT * FROM `benchmarks 2024 view` LIMIT 10;

-- Optional: Add specific WHERE clauses for filtering
-- SELECT * FROM `benchmarks 2024 view` WHERE segment = 'Technology';
-- SELECT * FROM `segment benchmarks 2024` WHERE segment = 'Healthcare';
