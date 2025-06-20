"""Minimal FastAPI application exposing AIS data."""

from __future__ import annotations

import json
import os

import aiosqlite
from fastapi import FastAPI, HTTPException
import uvicorn

DB_PATH = os.getenv("DB_PATH", "ais.db")

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/ais")
async def latest_ais() -> dict:
    """Return the latest AIS message from the database."""
    query = "SELECT timestamp, raw_message FROM ais_messages ORDER BY id DESC LIMIT 1"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query) as cursor:
            row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="No AIS messages available")

    timestamp, raw_message = row
    try:
        message = json.loads(raw_message)
    except json.JSONDecodeError:
        message = {"raw": raw_message}

    return {"timestamp": timestamp, "message": message}


def main() -> None:
    """Run the FastAPI app using uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
