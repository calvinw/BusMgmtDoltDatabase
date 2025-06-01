#!/bin/bash

TARGET_MODEL="google/gemini-2.5-flash-preview-05-20"
TARGET_COMPANY_NAME="Lululemon"
TARGET_YEAR=2023
TARGET_CIK="1397187"

echo "Running client for a single company:"
echo "Model: $TARGET_MODEL"
echo "Company: $TARGET_COMPANY_NAME"
echo "Year: $TARGET_YEAR"
echo "CIK: $TARGET_CIK"
echo "---"

# Execute the client script
# Ensure 'uv' is in your PATH and you are in the correct directory,
# or adjust the path to client.py accordingly.
uv run python client.py \
  --model "$TARGET_MODEL" \
  --company "$TARGET_COMPANY_NAME" \
  --year "$TARGET_YEAR" \
  --cik "$TARGET_CIK"

echo "---"
echo "Script finished."
