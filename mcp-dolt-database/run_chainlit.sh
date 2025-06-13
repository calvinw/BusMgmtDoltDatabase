#!/bin/bash

set -e

PORT=${PORT:-8080}
echo "🚀 Starting Chainlit app on port $PORT..."
uv run chainlit run .venv/lib/python3.13/site-packages/app.py --host 0.0.0.0 --port "$PORT"
