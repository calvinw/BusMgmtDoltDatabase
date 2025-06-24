import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add subdirectories to Python path
sys.path.append(str(Path(__file__).parent / "mcp-dolt-database"))
sys.path.append(str(Path(__file__).parent / "mcp-sec-10ks"))
sys.path.append(str(Path(__file__).parent / "mcp-yfinance-10ks"))

# Import each MCP server from its subdirectory
# Change to each directory and import to avoid naming conflicts
import importlib.util

# Import dolt server
dolt_path = Path(__file__).parent / "mcp-dolt-database" / "server.py"
spec = importlib.util.spec_from_file_location("dolt_server", dolt_path)
dolt_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dolt_module)
dolt_mcp = dolt_module.mcp

# Import sec server
sec_path = Path(__file__).parent / "mcp-sec-10ks" / "server.py"
spec = importlib.util.spec_from_file_location("sec_server", sec_path)
sec_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sec_module)
sec_mcp = sec_module.mcp

# Import yfinance server
yfinance_path = Path(__file__).parent / "mcp-yfinance-10ks" / "server.py"
spec = importlib.util.spec_from_file_location("yfinance_server", yfinance_path)
yfinance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yfinance_module)
yfinance_mcp = yfinance_module.mcp

# Create SSE apps for each MCP server (matching individual sse_server.py files)
dolt_http_app = dolt_mcp.http_app(transport="sse", path='/sse')
sec_http_app = sec_mcp.http_app(transport="sse", path='/sse')  
yfinance_http_app = yfinance_mcp.http_app(transport="sse", path='/sse')

# Minimal OAuth endpoint (just enough for Claude.ai)
async def oauth_metadata(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return JSONResponse({
        "issuer": base_url
    })

# Create main FastAPI app
app = FastAPI(
    title="Bus Management MCP Servers",
    description="Multiple MCP servers for business management database access",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Access-Control-Allow-Origin
    allow_methods=["GET", "POST", "OPTIONS"],  # Access-Control-Allow-Methods
    allow_headers=["Content-Type", "Authorization", "x-api-key"],  # Access-Control-Allow-Headers
    expose_headers=["Content-Type", "Authorization", "x-api-key"],  # Access-Control-Expose-Headers
    max_age=86400  # Access-Control-Max-Age (in seconds)
)

# Add the OAuth metadata route
app.add_api_route("/.well-known/oauth-authorization-server", oauth_metadata, methods=["GET"])

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Bus Management MCP Servers",
        "endpoints": [
            "https://bus-mgmt-servers.mcp.mathplosion.com/mcp-dolt-database/sse",
            "https://bus-mgmt-servers.mcp.mathplosion.com/mcp-sec-10ks/sse", 
            "https://bus-mgmt-servers.mcp.mathplosion.com/mcp-yfinance-10ks/sse"
        ]
    }

# Mount each MCP server at its respective path
app.mount("/mcp-dolt-database", dolt_http_app)
app.mount("/mcp-sec-10ks", sec_http_app)
app.mount("/mcp-yfinance-10ks", yfinance_http_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)