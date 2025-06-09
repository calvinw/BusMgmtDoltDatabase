# MCP Dolt Database 

This project is an example of an MCP server.

## Setup Instructions

1.  **Create and activate a virtual environment.**
    It's recommended to use a virtual environment to manage project dependencies. This project uses `uv`.

    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

2.  **Install dependencies.**
    This project uses `uv` for dependency management. Install the dependencies using the following command, which synchronizes your environment with the `pyproject.toml` and `uv.lock` files:
    ```bash
    uv sync
    ```

3.  **Run the project as local MCP.**
    The project can be run as local MCP using server.py:
    ```bash
    python server.py
    ```

4.  **Run the project as remote MCP.*
    The project can be run as a remote MCP using sse_server.py:
    ```bash
    python sse_server.py
    ```

    Type: SSE
    Name: mcp-dolt-database
    ServerURL: https://mcp-dolt-database-3b846e43fd3d.herokuapp.com/sse
