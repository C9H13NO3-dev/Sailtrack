"""Asynchronous AIS listener that stores messages to SQLite."""

from __future__ import annotations

import asyncio
import json
import traceback
import os
from datetime import datetime
from typing import Iterable

import aiosqlite
import websockets

AIS_WS_URL = os.getenv("AIS_WS_URL", "wss://stream.aisstream.io/v0/stream")
DB_PATH = os.getenv("DB_PATH", "/data/ais.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ais_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    mmsi INTEGER NOT NULL,
    raw_message TEXT NOT NULL
);
"""

INSERT_SQL = "INSERT INTO ais_messages (timestamp, mmsi, raw_message) VALUES (?, ?, ?)"


async def listen(api_key: str, mmsi_list: Iterable[int] | None = None) -> None:
    """Connect to aisstream.io and store messages in SQLite."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()

        subscription: dict[str, object] = {"APIKey": api_key}
        if mmsi_list:
            subscription["FiltersShipMMSI"] = [str(m) for m in mmsi_list]

        print(f"Connecting to {AIS_WS_URL}")
        async with websockets.connect(AIS_WS_URL) as ws:
            await ws.send(json.dumps(subscription))
            print(
                "Subscribed to AIS stream for %s"
                % (",".join(str(m) for m in mmsi_list) if mmsi_list else "all ships")
            )
            async for message in ws:
                try:
                    data = json.loads(message)
                    mmsi = int(data.get("MMSI", 0))
                    print(f"Received AIS message for MMSI {mmsi}")
                except Exception:
                    mmsi = 0
                    print(f"Failed to parse AIS message: {message}")
                    traceback.print_exc()
                try:
                    await db.execute(
                        INSERT_SQL,
                        (datetime.utcnow().isoformat(), mmsi, message),
                    )
                    await db.commit()
                except Exception:
                    print("Error storing AIS message")
                    traceback.print_exc()

async def main() -> None:
    api_key = os.getenv("AISSTREAM_API_KEY")
    if not api_key:
        raise SystemExit("AISSTREAM_API_KEY environment variable not set")
    mmsi_env = os.getenv("MMSI_LIST", "")
    mmsi_list = [int(m.strip()) for m in mmsi_env.split(",") if m.strip()] if mmsi_env else []
    print("Starting AIS listener")
    await listen(api_key, mmsi_list)

if __name__ == "__main__":
    asyncio.run(main())
