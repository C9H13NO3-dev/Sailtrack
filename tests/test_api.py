import os
import sys
import asyncio
import json
from importlib import reload
from pathlib import Path
from datetime import datetime

import aiosqlite
from fastapi.testclient import TestClient

# set env before importing api
os.environ["AISSTREAM_API_KEY"] = ""  # disable listener
SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

def get_app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DB_PATH"] = str(db_path)
    import sailtrack.api as api
    reload(api)
    return api, db_path

async def insert_sample(db_path, mmsi=123456789):
    import sailtrack.ais_listener as listener
    async with aiosqlite.connect(db_path) as db:
        await db.execute(listener.CREATE_TABLE_SQL)
        msg = {"MMSI": mmsi, "lat": 10.0, "lon": 20.0}
        await db.execute(listener.INSERT_SQL, (datetime.utcnow().isoformat(), mmsi, json.dumps(msg)))
        await db.commit()


def test_map_endpoint(tmp_path):
    api, db_path = get_app(tmp_path)
    asyncio.run(insert_sample(db_path))
    with TestClient(api.app) as client:
        response = client.get("/v1/map/123456789")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

