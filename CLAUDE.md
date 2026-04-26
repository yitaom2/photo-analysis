# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal photo library project that imports photos from iPhone/Android/cloud into a self-hosted [Immich](http://localhost:2283) instance, then visualizes GPS metadata on an interactive world map.

## Services

- **Immich**: `http://localhost:2283` — self-hosted photo manager (Docker)
- **Immich CLI**: `immich` (npm global) — for bulk uploads
- **immich-go**: alternative importer with better Google Takeout support

## Key Commands

```bash
# Start/stop Immich
cd ~/immich && docker compose up -d
cd ~/immich && docker compose down

# Upload photos via CLI
immich login http://localhost:2283 <API_KEY>
immich upload /path/to/photos

# Upload Google Takeout via immich-go
immich-go upload gp-takeout --server http://localhost:2283 --api-key <KEY> /path/to/takeout

# Run GPS export script
python export_gps.py   # outputs gps_data.json

# Backup Postgres DB
docker exec immich_postgres pg_dumpall -U postgres > backup_$(date +%Y%m%d).sql
```

## GPS Export Script

`export_gps.py` calls `POST /api/assets/search` (paginated, `size=1000`, `withExif=true`) and writes `gps_data.json`:

```json
[{ "lat": 0.0, "lng": 0.0, "date": "YYYY-MM-DD", "city": "", "country": "", "id": "<asset-uuid>" }]
```

The script requires `IMMICH_URL` and `API_KEY` constants at the top of the file.

## Map Visualization Stack

Planned: **Mapbox GL JS** or **Deck.gl + React**

Features to build:
- World map with photo location clusters
- Time-range slider to filter by date
- Click a city/cluster → show photo thumbnails (fetched via Immich `/api/assets/<id>/thumbnail`)

## Immich API Patterns

- Auth: `x-api-key` header
- Search assets: `POST /api/assets/search` with `{ page, size, withExif: true }`
- Thumbnail: `GET /api/assets/<id>/thumbnail?size=preview`
- Asset detail: `GET /api/assets/<id>`
