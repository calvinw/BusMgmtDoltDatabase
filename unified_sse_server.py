import os
import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn
import importlib.util

# Import the complete FastAPI apps from each subdirectory
def import_sse_app(subdirectory_name):
    """Import the FastAPI app from a subdirectory's sse_server.py"""
    # Add the subdirectory to Python path temporarily
    subdirectory_path = str(Path(__file__).parent / subdirectory_name)
    if subdirectory_path not in sys.path:
        sys.path.insert(0, subdirectory_path)
    
    try:
        sse_path = Path(__file__).parent / subdirectory_name / "sse_server.py"
        spec = importlib.util.spec_from_file_location(f"{subdirectory_name}_sse", sse_path)
        sse_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sse_module)
        return sse_module.app
    finally:
        # Remove from path to avoid conflicts
        if subdirectory_path in sys.path:
            sys.path.remove(subdirectory_path)

# Import the complete FastAPI apps from each subdirectory
dolt_app = import_sse_app("mcp-dolt-database")
sec_app = import_sse_app("mcp-sec-10ks")
yfinance_app = import_sse_app("mcp-yfinance-10ks")

# Minimal OAuth endpoint (just enough for Claude.ai)
async def oauth_metadata(request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "issuer": base_url
    }

# Create main FastAPI app
app = FastAPI(
    title="Bus Management MCP Servers",
    description="Multiple MCP servers for business management database access",
    version="1.0.0"
)

# Add the OAuth metadata route at root level for Claude.ai compatibility
from fastapi.responses import JSONResponse
from fastapi import Request

async def oauth_metadata_handler(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return JSONResponse({
        "issuer": base_url
    })

app.add_api_route("/.well-known/oauth-authorization-server", oauth_metadata_handler, methods=["GET"])

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

# Mount each complete FastAPI app at its respective path
app.mount("/mcp-dolt-database", dolt_app)
app.mount("/mcp-sec-10ks", sec_app)
app.mount("/mcp-yfinance-10ks", yfinance_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)