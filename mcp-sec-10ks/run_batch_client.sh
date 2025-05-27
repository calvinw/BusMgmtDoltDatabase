#!/bin/bash

# Run batch processing with companies.csv
uv run python batch_client.py \
  --model "google/gemini-2.5-flash-preview-05-20" \
  --csv companies.csv
