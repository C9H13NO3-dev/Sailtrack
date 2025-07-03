"""FastAPI application exposing AIS data."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

import aiosqlite
from fastapi import FastAPI, HTTPException, Response
from staticmap import StaticMap, CircleMarker
from PIL import Image
import io


def _extract_position(message: dict) -> tuple[float, float]:
    """Return latitude and longitude from an AIS message."""
    lat = None
    lon = None
    for key in ("lat", "latitude", "Lat", "LAT"):
        if key in message:
            lat = float(message[key])
            break
    for key in ("lon", "longitude", "Lon", "LON"):
        if key in message:
            lon = float(message[key])
            break
    if lat is None or lon is None:
        raise ValueError("Latitude/Longitude not found")
    return lat, lon

from . import ais_listener

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/ais.db")
AISSTREAM_API_KEY = os.getenv("AISSTREAM_API_KEY")
MMSI_ENV = os.getenv("MMSI_LIST", "")
MMSI_LIST = [int(m.strip()) for m in MMSI_ENV.split(",") if m.strip()] if MMSI_ENV else []

app = FastAPI(title="Sailtrack API", version="0.2")

@app.on_event("startup")
async def startup() -> None:
    logger.info("Starting API with database at %s", DB_PATH)
    app.state.db = await aiosqlite.connect(DB_PATH)
    await app.state.db.execute(ais_listener.CREATE_TABLE_SQL)
    await app.state.db.commit()
    if AISSTREAM_API_KEY:
        logger.info("Launching AIS listener background task")
        app.state.listener = asyncio.create_task(
            ais_listener.listen(AISSTREAM_API_KEY, MMSI_LIST)
        )

@app.on_event("shutdown")
async def shutdown() -> None:
    logger.info("Shutting down API")
    if getattr(app.state, "listener", None):
        app.state.listener.cancel()
    await app.state.db.close()

@app.get("/v1/ais/{mmsi}")
async def latest_ais(mmsi: int) -> dict:
    query = (
        "SELECT timestamp, raw_message FROM ais_messages WHERE mmsi=?"
        " ORDER BY id DESC LIMIT 1"
    )
    async with app.state.db.execute(query, (mmsi,)) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No data for MMSI")
    timestamp, raw_message = row
    try:
        message = json.loads(raw_message)
    except json.JSONDecodeError:
        message = {"raw": raw_message}
    return {"timestamp": timestamp, "message": message}


@app.get("/v1/map/{mmsi}")
async def map_image(
    mmsi: int,
    width: int = 600,
    height: int = 400,
    color_scheme: str = "colored",
) -> Response:
    """Return a static map image showing the vessel's last known position."""
    query = (
        "SELECT raw_message FROM ais_messages WHERE mmsi=? ORDER BY id DESC LIMIT 1"
    )
    async with app.state.db.execute(query, (mmsi,)) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No data for MMSI")
    try:
        message = json.loads(row[0])
        lat, lon = _extract_position(message)
    except Exception as exc:
        logger.exception("Failed to parse AIS position")
        raise HTTPException(status_code=500, detail="Invalid AIS data") from exc

    smap = StaticMap(
        width,
        height,
        url_template="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
    )
    smap.add_marker(CircleMarker((lon, lat), "#0033ff", 12))
    image = smap.render()
    if color_scheme == "grayscale":
        image = image.convert("L")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
