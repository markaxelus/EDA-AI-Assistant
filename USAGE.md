# Usage

## Setup
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Docker Compose
```bash
# Production
docker-compose --profile production up

# Development
docker-compose --profile development up -d

# Testing
docker-compose --profile test up
```

## Docker Registry
```bash
docker pull ghcr.io/markaxelus/eda-ai-assistant:main
docker run --rm --env-file .env -v $(pwd)/output:/app/output ghcr.io/markaxelus/eda-ai-assistant:main
```

## Output
- `output/report.md` - Analysis report
- `output/results.json` - Structured data
