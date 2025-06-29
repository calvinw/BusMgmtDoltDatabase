#!/bin/bash

# Array of your MCP directory names
mcp_dirs=("mcp-dolt-database" "mcp-sec-10ks" "mcp-yfinance-10ks")

for dir in "${mcp_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "Setting up $dir..."
        cd "$dir"
        uv sync
        cd ..
        echo "Completed $dir"
        echo "---"
    else
        echo "Directory $dir not found, skipping..."
    fi
done

echo "All MCP directories processed!"
