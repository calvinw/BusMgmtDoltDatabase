# MCP Server

This project is an example of an MCP server.

## Setup Instructions

1.  **Ensure Python 3.11 is installed.**
2.  **Create and activate a virtual environment.**
    It's recommended to use a virtual environment to manage project dependencies. This project uses `uv`.

    Using `uv`:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies.**
    This project uses `uv` for dependency management. Install the dependencies using the following command, which synchronizes your environment with the `pyproject.toml` and `uv.lock` files:
    ```bash
    uv sync
    ```

4.  **Run the project.**
    The project can be run using the provided script:
    ```bash
    sh run_inspector.sh
    ```
