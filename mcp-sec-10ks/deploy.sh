# Deploy from your current directory (minimal-remote-mcp)
gcloud run deploy minimal-remote-mcp \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
