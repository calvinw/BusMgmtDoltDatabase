#!/bin/bash

# Test single company to see detailed error messages
echo "Testing single company: Walmart"
uv run python client.py \
  --model "google/gemini-2.5-flash-preview-05-20" \
  --company "Walmart" \
  --year 2024 \
  --cik 104169
