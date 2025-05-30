
If you are just cloning the repo for the first time, since it has git submodules

```bash
git clone --recurse-submodules https://github.com/calvinw/BusMgmtDoltDatabase.git
```

Or if you already cloned the regular way you can do this:

```bash
git clone https://github.com/calvinw/BusMgmtDoltDatabase.git
cd BusMgmtDoltDatabase
git submodule update --init --recursive
```

This will load in the chainlit-mcp-client

Also if you want to load some of the MCPS as tools in the local chainlit app running in the chainlit-mcp-client directory:

## MCP greet server
```bash
../mcp-greet/.venv/bin/python ../mcp-greet/server.py
```

## MCP Dolt Database Server 
```bash
../mcp-dolt-database/.venv/bin/python ../mcp-dolt-database/server.py
```

## MCP Sec 10ks 
```bash
../mcp-sec-10ks/.venv/bin/python ../mcp-sec-10ks/server.py
```
