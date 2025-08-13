# 📦 Rekaz Drive

A lightweight, extensible service for storing and retrieving binary data (blobs) across **multiple storage backends** — including **Database, Filesystem, S3, and FTP** — with a consistent API interface.

---

## 🚀 Features

- **Multiple Storage Backends**
  - Database (SQLite, Postgres, etc.)
  - Filesystem
  - Amazon S3 (or S3-compatible)
  - FTP (with TLS support)

- **Atomicity Across All Storage Types**
  - Ensures that metadata and blob data are always in sync.
  - Prevents partial writes by committing data and metadata in one logical operation.

- **Unified API**
  - Simple, consistent endpoints for all storage types.
  - Supports switching storage by changing environment variables.

- **Security**
  - Bearer token authentication via `Authorization: Bearer <token>` header.

- **Dockerized**
  - Fully containerized for consistent environments.
  - One-command setup using `docker compose`.

- **Testing**
  - Comprehensive pytest suite for all storage backends.
  - `.env` preloaded with working values for quick testing.

---

## 🏗 Architecture

This project follows a **Hexagonal Architecture (Ports and Adapters)** design pattern:

- **Domain Layer**  
  Contains core business logic for blob operations, independent of any framework or storage technology.

- **Ports (Interfaces)**  
  Define the contract for storage operations (e.g., `StoragePort`) that any backend implementation must follow.

- **Adapters (Implementations)**  
  Concrete implementations for Database, Filesystem, S3, and FTP, each adhering to the same interface.

- **Benefits**
  - **Extensibility:** Add new storage backends without touching the domain logic.
  - **Testability:** Swap out adapters for mocks in tests without changing core code.
  - **Maintainability:** Clear separation of concerns keeps code organized and easy to modify.

---

## 📂 Project Structure
- Root Directory
- app/ - Application source code
- tests/ - Test suite
- .env - Environment variables (pre-filled for testing)
- Dockerfile - App container definition
- docker-compose.yml - Orchestration for app + dependencies
- requirements.txt - Python dependencies
- README.md - This file

---

## ⚙️ Environment Variables

The `.env` file is **included** and already configured for:
- Free-tier S3 bucket
- Free-tier FTP storage
- Local filesystem path
- Local SQLite DB

Example:

- AUTH_BEARER_TOKEN=dev-secret-123
- STORAGE=ftp
- FS_BASE_PATH=./storage
- DATABASE_URL=sqlite:///./metadata.db

- S3_ENDPOINT=https://s3.eu-north-1.amazonaws.com
- S3_REGION=eu-north-1
- S3_BUCKET=rekaz-s3
- S3_ACCESS_KEY=AKIA...
- S3_SECRET_KEY=...
- S3_FORCE_PATH_STYLE=false

- FTP_HOST=ftp.drivehq.com
- FTP_PORT=21
- FTP_USER=...
- FTP_PASSWORD=...
- FTP_TLS=true
- FTP_BASE_DIR=/
- FTP_TIMEOUT=12


---

## 🐳 Running with Docker Compose

**Build and start:**
```bash
docker compose up --build

Stop:

docker compose down

Once running, the service will be available at:
http://localhost:8000
🧪 Testing

Run tests inside the container:

docker compose run --rm app pytest

Run tests locally:

pytest

📡 API Usage

Create a Blob:

curl --location 'http://localhost:8000/v1/blobs' \
--header 'Authorization: Bearer dev-secret-123' \
--header 'Content-Type: application/json' \
--data '{"id":"k5","data":"SGVsbG54548="}'

Retrieve a Blob:

curl --location 'http://localhost:8000/v1/blobs/k5' \
--header 'Authorization: Bearer dev-secret-123'

📝 Reviewer Note

I took extra time to ensure the reviewer has a smooth setup and testing experience.
For this reason, I’ve kept the .env file with the actual values I used.
They are mostly free-tier storage services, so you can test and try all 
functionality right away without any additional configuration or setup steps.
(to test S3 storage, you will have to provide your own access tokens)