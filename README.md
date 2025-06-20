# Inkplate Sail Tracker

Lightweight end‑to‑end system for family & friends to follow a sailor in real time. Part 1 is a small Dockerized Python service that consumes AIS messages, draws the boat on an OpenSeaMap raster, and exposes a REST API. Part 2 is ultra‑low‑power firmware for the Inkplate 10 e‑Paper display that fetches the data and shows it elegantly in portrait mode.

---

## Features

* 🔌 **Zero‑friction deploy** – single Docker container, SQLite storage, no external database.
* 🌐 **Live AIS feed** – listens to [aisstream.io](https://aisstream.io) WebSocket, filtered by MMSI.
* 🗺️ **Auto‑generated map** – grabs OpenSeaMap tiles, draws a heading‑aware triangle icon, returns a PNG.
* 📡 **RESTful API** – `/ais`, `/map.png`, `/health` (with optional `/stats`).
* 💤 **Inkplate 10 support** – Wi‑Fi, deep‑sleep cycles, crisp portrait e‑paper layout.

---

## Quick‑Start (Developer)

```bash
# 1. Clone
$ git clone https://github.com/<you>/inkplate-sail-tracker.git
$ cd inkplate-sail-tracker

# 2. Build & run (adjust MMSI & API key)
$ docker build -t sail-tracker .
$ docker run -e MMSI=123456789 -e AISSTREAM_API_KEY=<token> -p 8000:8000 sail-tracker

# 3. Explore
Open http://localhost:8000/docs for the interactive Swagger UI.
```

### Runtime Environment Variables

| Name                | Purpose                             | Default |
| ------------------- | ----------------------------------- | ------- |
| `MMSI`              | Vessel MMSI to track                | —       |
| `AISSTREAM_API_KEY` | Token from aisstream.io             | —       |
| `MAP_RADIUS_NM`     | Half‑width of map in nautical miles | `12`    |
| `TILE_CACHE_MIN`    | Minutes to cache OpenSeaMap tiles   | `30`    |

---

## REST API Overview

| Method | Path       | Description                          |
| ------ | ---------- | ------------------------------------ |
| GET    | `/ais`     | Latest AIS message in JSON           |
| GET    | `/map.png` | 1024 × 1024 PNG with vessel triangle |
| GET    | `/stats`   | (opt) simple statistics JSON         |
| GET    | `/health`  | Liveness probe                       |

---

## Firmware Sketch (Inkplate 10)

* Located under `/firmware` (PlatformIO project).
* `config.h` defines Wi‑Fi creds & API base URL.
* Refresh interval defaults to **5 min** → deep‑sleep to save battery.
* Uses Inkplate library + ArduinoJSON.

---

## Architecture

```text
+-------------+      WebSocket      +------------------+
| aisstream.io| ───────────────────▶| Python Service   |
+-------------+                     | FastAPI + SQLite |
                                     +------------------+
                                              ▲ REST
                                              ▼
                                     +------------------+
                                     | Inkplate 10 MCU  |
                                     +------------------+
```

---

## Roadmap / Progress Tracker

> Tick items as they are completed. Each milestone should be merged via Pull Request.

### Milestone 1 – AIS Listener (Python)

* [ ] Create minimal `pyproject.toml` / `requirements.txt`
* [ ] Connect to aisstream.io WebSocket
* [ ] Persist messages to SQLite (`ais_messages` table)

### Milestone 2 – REST API Skeleton

* [ ] Scaffold FastAPI app & `/health`
* [ ] `/ais` endpoint returning latest row

### Milestone 3 – Map Rendering

* [ ] Compute bounding box from last known position
* [ ] Fetch OpenSeaMap tiles & stitch
* [ ] Draw bearing‑aware triangle marker
* [ ] Expose `/map.png` endpoint

### Milestone 4 – Containerization & CI

* [ ] Multi‑stage `Dockerfile` (slim base)
* [ ] GitHub Action: lint ► test ► image build ► push (GHCR)

### Milestone 5 – Statistics Layer (optional)

* [ ] Average SOG (6 h)
* [ ] Distance travelled (24 h)

### Milestone 6 – Inkplate Firmware

* [ ] Wi‑Fi connect & OTA config
* [ ] Fetch `/map.png` & `/ais`
* [ ] Render portrait layout (compass, SOG, COG, time)
* [ ] Power‑save deep sleep cycle

### Milestone 7 – Polishing

* [ ] Robust error handling & retries
* [ ] Bind mount for persistent DB volume
* [ ] README badges & screenshots

---

## Contributing

1. Fork the repo & create a feature branch.
2. Commit your changes with clear messages.
3. Open a Pull Request; link to an open issue or start a discussion.

All contributions should pass linting (`ruff`), type checks (`mypy`), and unit tests.

---

## License

Released under the MIT License. AIS data and map tiles are subject to their respective provider licenses.

> **Disclaimer**: This project is **not for navigation**. Data and map accuracy are not guaranteed. Use at your own risk.
