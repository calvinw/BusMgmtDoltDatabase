
# STDIO MCP SERVERS

Also if you want to load some of the MCPS (STDIO mode) as tools in the local chainlit app running in the chainlit-mcp-client directory:

First run this:
```bash
./run_chainlit.sh
```

Hit the MCP plug and add in these servers as Type STDIO:

```bash
# MCP greet server
../mcp-greet/.venv/bin/python ../mcp-greet/server.py

# MCP dolt database 
../mcp-dolt-database/.venv/bin/python ../mcp-dolt-database/server.py

# MCP Sec 10ks 
../mcp-sec-10ks/.venv/bin/python ../mcp-sec-10ks/server.py

# MCP yFinance 10ks 
../mcp-yfinance-10ks/.venv/bin/python ../mcp-yfinance-10ks/server.py
```
