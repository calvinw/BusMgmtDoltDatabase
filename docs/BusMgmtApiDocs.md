# BusMgmtBenchmarks REST API Documentation with Live Results

This document provides comprehensive examples of using the DoltHub REST API to access the calvinw/BusMgmtBenchmarks database, including actual JSON responses from the API.

*Generated automatically by processing 0 API queries*

# BusMgmtBenchmarks REST API Documentation

This document provides comprehensive examples of using the DoltHub REST API to access the `calvinw/BusMgmtBenchmarks` database. The API returns data in JSON format and is perfect for building web applications that need financial benchmarking data.

## Base URL Structure

All API calls follow this pattern:
```

## API Queries and Responses

The following sections show each API query along with its actual JSON response and explanation.

## Summary

- Total queries processed: 0
- Successful queries: 0
- Failed queries: 0

## Helper Functions

```javascript
function buildBenchmarkQuery(sqlQuery) {
  const baseUrl = 'https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks';
  const encodedQuery = encodeURIComponent(sqlQuery);
  return `${baseUrl}?q=${encodedQuery}`;
}

// Example usage:
const url = buildBenchmarkQuery("SELECT * FROM new_company_info WHERE segment = 'Technology'");
```
