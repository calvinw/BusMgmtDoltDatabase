# uv run python client.py \
#   --model "google/gemini-2.5-flash-preview-05-20" \
#   --company "Costco" \
#   --year 2023 \
#   --cik 909832
# --company "Lululemon" \
# --year 2023 \
# --cik 1397187 
uv run python client.py \
  --model "google/gemini-2.5-flash-preview-05-20" \
  --csv companies-small.csv
