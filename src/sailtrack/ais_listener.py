"""Asynchronous AIS listener that stores messages to SQLite."""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional

import websockets
import aiosqlite

AIS_WS_URL = "wss://stream.aisstream.io/v0/stream"
DB_PATH = os.getenv("DB_PATH", "ais.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ais_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    raw_message TEXT NOT NULL
);
"""

INSERT_SQL = "INSERT INTO ais_messages (timestamp, raw_message) VALUES (?, ?)"

async def listen(api_key: str, mmsi: Optional[int] = None) -> None:
    """Connect to aisstream.io and store messages in SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()

        headers = {}
        subscription = {"APIKey": api_key}
        if mmsi:
            subscription["FilterMMSI"] = [str(mmsi)]

        async with websockets.connect(AIS_WS_URL, extra_headers=headers) as ws:
            await ws.send(json.dumps(subscription))
            async for message in ws:
                await db.execute(INSERT_SQL, (datetime.utcnow().isoformat(), message))
                await db.commit()

async def main() -> None:
    api_key = os.getenv("AISSTREAM_API_KEY")
    if not api_key:
        raise SystemExit("AISSTREAM_API_KEY environment variable not set")
    mmsi = os.getenv("MMSI")
    await listen(api_key, int(mmsi) if mmsi else None)

if __name__ == "__main__":
    asyncio.run(main())
