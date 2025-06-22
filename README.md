# Dockerized AIS Tracker Service

A lightweight, Dockerized Python service that connects to **aisstream.io** via WebSocket to track vessel positions (MMSI), persists data in a SQLite database, and exposes a REST API for querying the latest AIS data, generating map images, and retrieving statistics.

---

## 🚀 Project Goals

1. **Reliable Data Ingestion**: Connect to aisstream.io WebSocket API and continuously ingest AIS messages for one or more configured MMSIs.
2. **Persistence**: Store incoming messages efficiently in an embedded SQLite database within the container.
3. **RESTful API**:

   * **Latest Data**: Retrieve the most recent AIS record for a given MMSI.
   * **Map Generation**: Produce a PNG or JPEG map (via OpenSeaMap) showing vessel position, customizable by size and color scheme (grayscale or colored).
   * **Statistics**: Calculate and return metrics over the past 24 hours (e.g., total distance traveled, average speed over ground).
4. **Containerization**: Provide a Dockerfile for easy deployment, environment configuration, and scaling.
5. **Configuration**: Allow configuration of:

   * Target MMSI list
   * Database file path
   * Map image parameters (size defaults, color scheme)
   * WebSocket endpoint and reconnect settings
6. **Testing & CI**: Include unit and integration tests, plus a CI pipeline for linting, building, and pushing the Docker image.

---

## 📦 Features

* **WebSocket Client** for aisstream.io
* **SQLite** persistence layer with simple ORM (e.g., SQLAlchemy)
* **FastAPI**-based REST endpoints
* **Map Rendering** via `staticmap` or similar against OpenSeaMap tiles
* **Statistics Engine** for distance and SOG aggregations
* **Dockerized** for one-command startup
* **Configuration** via environment variables or `.env`

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **Web Framework**: FastAPI
* **Database**: SQLite + SQLAlchemy
* **WebSocket**: `websockets` or `aiohttp`
* **Mapping**: `staticmap` or `folium` with OpenSeaMap tiles
* **Container**: Docker + Docker Compose (optional)
* **Testing**: Pytest
* **CI**: GitHub Actions

---

## 📅 Roadmap & Milestones

### v0.1 — MVP

* [x] WebSocket client to aisstream.io with configurable MMSI list
* [x] Persist raw AIS messages to SQLite
* [x] `GET /v1/ais/{mmsi}`: return latest AIS record
* [x] Basic Dockerfile and `docker build`
* [x] Docker Compose for local dev
* [x] Documentation (this README)

### v0.2 — Extended Functionality

* [ ] `GET /v1/map/{mmsi}`: render static map with vessel position
* [ ] Support image parameters (`width`, `height`, `color_scheme`)
* [ ] Unit tests for ingestion and API

### v0.3 — Statistics & Polishing

* [ ] `GET /v1/stats/{mmsi}`: compute 24h distance and average SOG
* [ ] Integration tests (end-to-end)
* [ ] CI pipeline: lint, test, build, push
* [ ] Configuration validation and error handling

### v1.0 — Release

* [ ] Release-ready Docker image on Docker Hub
* [ ] Example `docker-compose.yaml`
* [ ] Full documentation
* [ ] Performance optimizations

---

## ✅ Task Breakdown

1. **Setup & Boilerplate**

   * Initialize Git repository
   * Create virtualenv, dependencies in `pyproject.toml`
   * Base FastAPI app scaffold
2. **WebSocket Ingestion**

   * Implement connector module
   * Configure reconnect and error backoff
   * Define data models and ORM
3. **Database Layer**

   * SQLAlchemy models for AIS message table
   * Migration or initial schema script
4. **API Endpoints**

   * Latest AIS data endpoint
   * Map generation endpoint
   * Statistics endpoint
5. **Mapping Integration**

   * Tile downloader or tile service wrapper
   * Static map generation logic
6. **Testing**

   * Unit tests for each module
   * Fixtures for sample AIS data
   * Mock WebSocket server
7. **Dockerization**

   * Write Dockerfile, define runtime configs
   * Docker Compose configuration
8. **CI/CD**

   * GitHub Actions workflow
   * Automated build and push steps
9. **Documentation & Examples**

   * README updates
   * Usage examples (cURL, Python client snippets)

---

## 👷‍♂️ Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-org/ais-tracker.git
   cd ais-tracker
   ```

2. **Configure** (via `.env` or env vars)

   ```ini
   AISSTREAM_API_KEY=<your_api_key>
   MMSI_LIST=123456789,987654321
   DB_PATH=/data/ais.db
   ```

3. **Docker build & run**

   ```bash
   docker build -t sailtrack:latest .
   docker run -d --env-file .env -p 8000:8000 sailtrack:latest
   ```

4. **Docker Compose**

   ```bash
   cp .env.example .env
   docker compose up --build
   ```

5. **Use the API**

   * Latest data: `GET http://localhost:8000/v1/ais/123456789`
   * Map: `GET http://localhost:8000/v1/map/123456789?width=800&height=600&color=grayscale`
   * Stats: `GET http://localhost:8000/v1/stats/123456789`

---

## 📄 License

MIT © Your Name or Org
