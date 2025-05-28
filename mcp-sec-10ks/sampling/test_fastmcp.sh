#!/bin/bash

# Test FastMCP sampling with a simple question
echo "Testing FastMCP sampling..."
uv run python fastmcp_client.py \
  --model "google/gemini-2.5-flash-preview-05-20" \
  --question "What is the capital of France and why is it important?"
