# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a business management database system built around three MCP (Model Context Protocol) servers that provide financial data access through APIs. The project integrates with DoltHub databases and financial data sources to provide comprehensive business analytics.

## Architecture

The system consists of three main MCP servers, each containerized and deployable independently:

1. **mcp-dolt-database**: Primary database interface for querying DoltHub databases containing financial metrics and company information
2. **mcp-sec-10ks**: SEC 10-K filing data access server
3. **mcp-yfinance-10ks**: Yahoo Finance integration for financial data

These servers are unified through `unified_sse_server.py` which combines all three MCP servers into a single FastAPI application with SSE (Server-Sent Events) transport.

## Core Database Schema

The primary database (`calvinw/BusMgmtBenchmarks/main`) contains:
- `financials`: Raw financial data for companies
- `company_info`: Company details with segment/subsegment classifications
- `financial_metrics`: Calculated financial ratios and metrics
- `segment_metrics`: Benchmark metrics aggregated by segment
- `subsegment_metrics`: Benchmark metrics aggregated by subsegment

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies for all MCP servers
./setup_mcps.sh

# Setup individual MCP server (run from project root)
cd mcp-dolt-database && uv sync && cd ..
cd mcp-sec-10ks && uv sync && cd ..
cd mcp-yfinance-10ks && uv sync && cd ..
```

### Running Servers
```bash
# Run unified server (all three MCP servers combined)
python unified_sse_server.py

# Run individual MCP servers
cd mcp-dolt-database && python sse_server.py
cd mcp-sec-10ks && python sse_server.py
cd mcp-yfinance-10ks && python sse_server.py
```

### Database Operations
```bash
# Run SQL queries (from sql/ directory)
cd sql && ./run_query.sh

# Update financial metrics
cd sql && ./update_metrics.sh
```

### Deployment
```bash
# Deploy to Google Cloud Run (run from individual MCP directories)
cd mcp-dolt-database && ./deploy-gcloud.sh
cd mcp-sec-10ks && ./deploy-gcloud.sh
cd mcp-yfinance-10ks && ./deploy-gcloud.sh

# Deploy to Heroku (run from individual MCP directories)
cd mcp-dolt-database && ./deploy_heroku.sh
```

## Key Configuration

- **Project ID**: `mcp-servers-20250621` (Google Cloud)
- **Region**: `us-central1`
- **Python Version**: >=3.13 (specified in pyproject.toml)
- **Main Dependencies**: fastmcp, fastapi, requests, uvicorn

## Architecture Notes

Each MCP server follows the same pattern:
- `*_server.py`: Core MCP server with tools and resources (dolt_server.py, sec_server.py, yfinance_server.py)
- `sse_server.py`: SSE transport wrapper
- `pyproject.toml`: Python dependencies and build configuration
- `cloudbuild.yaml`: Google Cloud Build configuration
- `Dockerfile`: Container configuration

The `unified_sse_server.py` imports all three servers dynamically and exposes them through different endpoints while maintaining OAuth compatibility for Claude.ai integration.

## Database Query Examples

The default database connection uses `calvinw/BusMgmtBenchmarks/main` format. Key query patterns are documented in the `docs/` directory and example responses are stored in `docs/api_responses/`.