#!/usr/bin/env python3
"""
BusMgmt Benchmarks API Query Tester

This script executes sample queries from the RestApiBusMgmtDoltDatabase.md documentation
and saves the JSON responses to show the API response structure.
"""

import requests
import json
import urllib.parse
import os
from typing import Dict, Any, List
import time

class BusMgmtAPITester:
    def __init__(self):
        self.base_url = "https://www.dolthub.com/api/v1alpha1/calvinw/BusMgmtBenchmarks"
        self.output_dir = "api_responses"
        self.sample_queries = self._define_sample_queries()
        
    def _define_sample_queries(self) -> List[Dict[str, str]]:
        """Define a comprehensive set of sample queries from the documentation"""
        return [
            {
                "name": "show_tables",
                "description": "Get all tables in the database",
                "query": "SHOW TABLES"
            },
            {
                "name": "company_info_all",
                "description": "Get all companies with segments and subsegments",
                "query": "SELECT company, display_name, ticker_symbol, segment, subsegment FROM new_company_info ORDER BY segment, display_name LIMIT 10"
            },
            {
                "name": "company_info_grocery",
                "description": "Find companies in Grocery segment",
                "query": "SELECT * FROM new_company_info WHERE segment = 'Grocery' ORDER BY display_name"
            },
            {
                "name": "company_by_ticker",
                "description": "Get company info by ticker symbol",
                "query": "SELECT * FROM new_company_info WHERE ticker_symbol = 'WMT'"
            },
            {
                "name": "financials_walmart_2023",
                "description": "Get financial data for Walmart in 2023",
                "query": "SELECT * FROM financials WHERE company_name = 'Walmart Inc.' AND year = 2023"
            },
            {
                "name": "revenue_data_2023",
                "description": "Get revenue data for all companies in 2023",
                "query": "SELECT company_name, year, `Net Revenue`, `Gross Margin`, `Operating Profit`, `Net Profit` FROM financials WHERE year = 2023 ORDER BY `Net Revenue` DESC LIMIT 10"
            },
            {
                "name": "walmart_multiyear",
                "description": "Get multi-year financial data for Walmart",
                "query": "SELECT company_name, year, `Net Revenue`, `Operating Profit` FROM financials WHERE company_name = 'Walmart Inc.' AND year >= 2020 ORDER BY year"
            },
            {
                "name": "amazon_metrics_2023",
                "description": "Get financial ratios for Amazon in 2023",
                "query": "SELECT * FROM new_financial_metrics WHERE company_name = 'Amazon.com Inc.' AND year = 2023"
            },
            {
                "name": "profitability_metrics_2023",
                "description": "Get profitability metrics for all companies in 2023",
                "query": "SELECT company_name, year, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM new_financial_metrics WHERE year = 2023 ORDER BY Return_on_Assets DESC LIMIT 10"
            },
            {
                "name": "efficiency_ratios_2023",
                "description": "Get efficiency ratios for companies in 2023",
                "query": "SELECT company_name, Asset_Turnover, Inventory_Turnover, Current_Ratio, Quick_Ratio FROM new_financial_metrics WHERE year = 2023 ORDER BY Asset_Turnover DESC LIMIT 10"
            },
            {
                "name": "segment_benchmarks_2023",
                "description": "Get benchmark metrics for all segments in 2023",
                "query": "SELECT * FROM segment_metrics WHERE year = 2023 ORDER BY segment"
            },
            {
                "name": "grocery_segment_benchmark",
                "description": "Get specific Grocery segment benchmark",
                "query": "SELECT segment, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage, Net_Profit_Margin_Percentage, Return_on_Assets FROM segment_metrics WHERE segment = 'Grocery' AND year = 2023"
            },
            {
                "name": "segment_profitability_comparison",
                "description": "Compare all segment benchmarks by profitability",
                "query": "SELECT segment, Operating_Profit_Margin_Percentage, Return_on_Assets FROM segment_metrics WHERE year = 2023 ORDER BY Return_on_Assets DESC"
            },
            {
                "name": "subsegment_benchmarks_2023",
                "description": "Get subsegment benchmarks for 2023",
                "query": "SELECT * FROM subsegment_metrics WHERE year = 2023 ORDER BY subsegment LIMIT 10"
            },
            {
                "name": "retail_subsegments",
                "description": "Get retail-related subsegments",
                "query": "SELECT subsegment, Gross_Margin_Percentage, Operating_Profit_Margin_Percentage FROM subsegment_metrics WHERE year = 2023 AND subsegment LIKE '%Retail%'"
            },
            {
                "name": "walmart_benchmarks_view",
                "description": "Get comprehensive Walmart data using benchmarks view",
                "query": "SELECT * FROM `benchmarks 2023 view` WHERE company = 'Walmart Inc.'"
            },
            {
                "name": "grocery_companies_metrics",
                "description": "Get all companies in Grocery segment with their metrics",
                "query": "SELECT company, segment, `Net Revenue`, `Gross Margin %`, `Operating Profit Margin %`, `Return on Assets` FROM `benchmarks 2023 view` WHERE segment = 'Grocery' ORDER BY `Net Revenue` DESC"
            },
            {
                "name": "top_companies_by_revenue",
                "description": "Get top companies by revenue across all segments",
                "query": "SELECT company, segment, `Net Revenue`, `Return on Assets` FROM `benchmarks 2023 view` ORDER BY `Net Revenue` DESC LIMIT 10"
            },
            {
                "name": "amazon_growth_trends",
                "description": "Get revenue growth trends for Amazon",
                "query": "SELECT company_name, year, Sales_Current_Year_vs_LY, Three_Year_Revenue_CAGR FROM new_financial_metrics WHERE company_name = 'Amazon.com Inc.' AND year >= 2020 ORDER BY year"
            },
            {
                "name": "grocery_peer_comparison",
                "description": "Compare multiple companies within Grocery segment",
                "query": "SELECT c.display_name, c.segment, m.Gross_Margin_Percentage, m.Operating_Profit_Margin_Percentage, m.Return_on_Assets FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE c.segment = 'Grocery' AND m.year = 2023 ORDER BY m.Return_on_Assets DESC"
            },
            {
                "name": "top_performers_roa",
                "description": "Find top performing companies by Return on Assets",
                "query": "SELECT c.display_name, c.segment, m.Return_on_Assets, m.Net_Profit_Margin_Percentage FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE m.year = 2023 AND m.Return_on_Assets IS NOT NULL ORDER BY m.Return_on_Assets DESC LIMIT 10"
            },
            {
                "name": "liquidity_ratios",
                "description": "Get liquidity ratios for companies",
                "query": "SELECT c.display_name, c.segment, m.Current_Ratio, m.Quick_Ratio, m.Debt_to_Equity FROM new_financial_metrics m JOIN new_company_info c ON m.company_name = c.company WHERE m.year = 2023 AND m.Current_Ratio IS NOT NULL ORDER BY m.Current_Ratio DESC LIMIT 10"
            },
            {
                "name": "search_walmart",
                "description": "Search for companies by name (Walmart)",
                "query": "SELECT display_name, ticker_symbol, segment FROM new_company_info WHERE display_name LIKE '%Walmart%'"
            },
            {
                "name": "available_segments",
                "description": "Get all available segments",
                "query": "SELECT DISTINCT segment FROM new_company_info WHERE segment IS NOT NULL ORDER BY segment"
            },
            {
                "name": "available_subsegments",
                "description": "Get all subsegments",
                "query": "SELECT DISTINCT subsegment FROM new_company_info WHERE subsegment IS NOT NULL ORDER BY subsegment LIMIT 15"
            }
        ]

    def build_url(self, sql_query: str) -> str:
        """Build the API URL with proper encoding"""
        encoded_query = urllib.parse.quote(sql_query)
        return f"{self.base_url}?q={encoded_query}"

    def execute_query(self, query_info: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single query and return the response"""
        url = self.build_url(query_info["query"])
        
        try:
            print(f"Executing: {query_info['name']} - {query_info['description']}")
            print(f"Query: {query_info['query'][:100]}{'...' if len(query_info['query']) > 100 else ''}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Add metadata to the result
            result['_metadata'] = {
                'query_name': query_info['name'],
                'description': query_info['description'],
                'original_query': query_info['query'],
                'api_url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"✓ Success: {len(result.get('rows', []))} rows returned")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Request Error: {e}")
            return {
                'query_execution_status': 'Error',
                'query_execution_message': str(e),
                'schema': None,
                'rows': None,
                '_metadata': {
                    'query_name': query_info['name'],
                    'description': query_info['description'],
                    'original_query': query_info['query'],
                    'error': str(e),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        except json.JSONDecodeError as e:
            print(f"✗ JSON Decode Error: {e}")
            return {
                'query_execution_status': 'Error',
                'query_execution_message': f'JSON decode error: {e}',
                'schema': None,
                'rows': None,
                '_metadata': {
                    'query_name': query_info['name'],
                    'description': query_info['description'],
                    'original_query': query_info['query'],
                    'error': f'JSON decode error: {e}',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }

    def save_response(self, query_name: str, response: Dict[str, Any]) -> None:
        """Save the response to a JSON file"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        filename = f"{self.output_dir}/{query_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f"  Saved to: {filename}")

    def create_summary_report(self, results: List[Dict[str, Any]]) -> None:
        """Create a summary report of all queries"""
        summary_file = f"{self.output_dir}/query_summary.json"
        
        summary = {
            'execution_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_queries': len(results),
            'successful_queries': len([r for r in results if r.get('query_execution_status') == 'Success']),
            'failed_queries': len([r for r in results if r.get('query_execution_status') != 'Success']),
            'queries': []
        }
        
        for result in results:
            metadata = result.get('_metadata', {})
            query_summary = {
                'name': metadata.get('query_name', 'unknown'),
                'description': metadata.get('description', ''),
                'status': result.get('query_execution_status', 'Unknown'),
                'row_count': len(result.get('rows', [])) if result.get('rows') else 0,
                'column_count': len(result.get('schema', [])) if result.get('schema') else 0,
                'error_message': result.get('query_execution_message', '') if result.get('query_execution_status') != 'Success' else None
            }
            summary['queries'].append(query_summary)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nSummary report saved to: {summary_file}")

    def create_consolidated_output(self, results: List[Dict[str, Any]]) -> None:
        """Create a single consolidated file with all responses for easy sharing"""
        consolidated_file = f"{self.output_dir}/all_responses_consolidated.json"
        
        consolidated = {
            'execution_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_queries': len(results),
                'successful_queries': len([r for r in results if r.get('query_execution_status') == 'Success']),
                'failed_queries': len([r for r in results if r.get('query_execution_status') != 'Success'])
            },
            'responses': {}
        }
        
        # Add all individual responses
        for result in results:
            metadata = result.get('_metadata', {})
            query_name = metadata.get('query_name', 'unknown')
            consolidated['responses'][query_name] = result
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)
        
        print(f"Consolidated output saved to: {consolidated_file}")
        print(f"📋 SHARE THIS FILE: You can share '{consolidated_file}' - it contains all responses in one file")

    def run_all_queries(self, delay_seconds: float = 1.0) -> None:
        """Execute all sample queries and save responses"""
        print(f"Starting execution of {len(self.sample_queries)} queries...")
        print(f"Results will be saved to: {self.output_dir}/\n")
        
        results = []
        
        for i, query_info in enumerate(self.sample_queries, 1):
            print(f"\n[{i}/{len(self.sample_queries)}]", end=" ")
            
            result = self.execute_query(query_info)
            results.append(result)
            
            self.save_response(query_info['name'], result)
            
            # Add delay between requests to be respectful
            if i < len(self.sample_queries):
                time.sleep(delay_seconds)
        
        # Create summary report
        self.create_summary_report(results)
        
        # Create consolidated output file
        self.create_consolidated_output(results)
        
        # Print final summary
        successful = len([r for r in results if r.get('query_execution_status') == 'Success'])
        failed = len(results) - successful
        
        print(f"\n{'='*60}")
        print(f"Execution Complete!")
        print(f"Total Queries: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Results saved in: {self.output_dir}/")
        print(f"{'='*60}")

    def run_single_query(self, query_name: str) -> None:
        """Execute a single query by name"""
        query_info = next((q for q in self.sample_queries if q['name'] == query_name), None)
        
        if not query_info:
            print(f"Query '{query_name}' not found.")
            print("Available queries:")
            for q in self.sample_queries:
                print(f"  - {q['name']}: {q['description']}")
            return
        
        print(f"Executing single query: {query_name}")
        result = self.execute_query(query_info)
        self.save_response(query_name, result)
        
        print(f"\nResult saved to: {self.output_dir}/{query_name}.json")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test BusMgmt Benchmarks API queries')
    parser.add_argument('--query', help='Execute a specific query by name')
    parser.add_argument('--list', action='store_true', help='List all available queries')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    tester = BusMgmtAPITester()
    
    if args.list:
        print("Available queries:")
        for query in tester.sample_queries:
            print(f"  {query['name']}: {query['description']}")
    elif args.query:
        tester.run_single_query(args.query)
    else:
        tester.run_all_queries(args.delay)

if __name__ == "__main__":
    main()
