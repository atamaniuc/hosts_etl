# 🧪 Host Data ETL Pipeline

A simple Python ETL pipeline that processes host data from `Qualys` and `Crowdstrike` APIs with "hybrid" pagination, deduplication, and MongoDB storage.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- API token for Silk Security API

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:atamaniuc/hosts_etl.git
   cd armis
   ```

2. **Run the complete setup:**
   ```bash
   make install
   ```
   This will:
   - Request your API token (The system uses Silk API endpoints for both Qualys and Crowdstrike data.)
   You can find your API token in the [profile](https://recruiting.app.silk.security/profile) page.
   - Create `.env` file
   - Build Docker images
   - Start services
   - Run the ETL pipeline

## 🛠️ Available Commands

Run `make help` to see all available commands with descriptions.

### Build and Infrastructure
- `make build` - Build the Docker image
- `make up` - Start all services in background
- `make down` - Stop and remove all containers
- `make start` - Start existing containers
- `make stop` - Stop running containers

### Pipeline Execution
- `make install` - Complete setup and run pipeline
- `make run` - Run the ETL pipeline

### Testing and Quality
- `make test` - Run all unit tests
- `make coverage` - Run tests with coverage
- `make lint` - Run pylint checks
- `make format` - Format code with Black
- `make type-check` - Run mypy type checking
- `make check-all-linters` - Run all quality checks

### Monitoring
- `make logs` - View application logs
- `make shell` - Open shell in container

## 🚀 Hybrid Pagination Strategy

- API supports only `limit=1` and `limit=2`, returns 500 for higher values.
- With `limit=2`, last host can be skipped.
- Hybrid approach: use `limit=2` for most pages, then `limit=1` for the last host.
- Result: all hosts fetched with minimal requests and robust error handling.

| Strategy      | Requests | Hosts | Performance |
|--------------|----------|-------|-------------|
| page_size=1  | 7        | 7     | Slow        |
| page_size=2  | 3        | 6     | Fast, incomplete |
| **Hybrid**   | **4**    | **7** | **Optimal** |

## 🧱 Architecture Overview

```
                +------------------------+
                |    Qualys API (JSON)   |
                +-----------+------------+
                           |
                           v
                +------------------------+
                | Crowdstrike API (JSON) |
                +----------+-------------+
                           |
                           v
                      [ Extractors ]
                    (Hybrid Pagination)
                           |
                           v
                    [ Normalizers ]
                           |
                           v
                 [ Deduplication Logic ]
                           |
                           v
                +----------------------+
                |    MongoDB Storage   |
                +----------+-----------+
                           |
                           v
                  [ Visualizations ]
```

**Modules:**
- `fetchers/` – API data downloaders with hybrid pagination
- `processors/` – normalization + deduplication
- `storage/` – MongoDB upsert and indexing
- `visualizations/` – PNG charts for OS distribution and host freshness
- `main.py` – the orchestration entry point

## 📊 Pipeline Architecture

1. **Extract**: Fetch hosts from Qualys & Crowdstrike using hybrid pagination.
2. **Transform**: Normalize to unified schema, deduplicate by (ip, hostname).
3. **Load**: Batch upsert to MongoDB (bulk_write, index).
4. **Visualize**: Generate PNG charts (OS, source, freshness).

## 🧪 Testing

Run the complete test suite:
```bash
make test
```

Run with coverage:
```bash
make coverage
```

## 📈 Monitoring

View real-time logs:
```bash
make logs
```

Access container shell:
```bash
make shell
```

## 🔍 Code Quality

The project maintains high code quality standards:

- **Pylint**: 10.00/10 score
- **Black**: Consistent code formatting
- **MyPy**: Type checking
- **Pytest**: Comprehensive test coverage

Run all quality checks:
```bash
make check-all-linters
```

## 🚀 Scalability Plan

- **Extract**: To scale: async fetching, message queues, rate limiting.
- **Transform**: To scale: batch processing, parallel normalization, aggregation.
- **Load**: To scale: sharding, buffered/streaming insert.
- **Visualization**: To scale: pre-aggregation, scheduled jobs, dashboards.

## ✅ Completed Features

- [x] Fetch and normalize Qualys data
- [x] Fetch and normalize Crowdstrike data
- [x] **Implement hybrid pagination strategy**
- [x] Deduplicate and merge records
- [x] Store to MongoDB with upserts
- [x] **Batch upsert to MongoDB (bulk_write)**
- [x] Create indexes for key fields
- [x] Generate visualizations (OS & freshness)
- [x] Unit tests with `pytest`
- [x] Dockerized pipeline
- [x] Add logging and error handling
- [x] Code quality tools (pylint, black, mypy)
- [x] Comprehensive Makefile with help
- [x] API token management

## 📎 Tech Stack

- **Python 3.10**
- **MongoDB**
- `requests`, `pymongo`, `matplotlib`, `python-dotenv`
- `pytest` for testing
- Docker + Docker Compose
- `make` for automation

## 📈 Visualizations

The pipeline generates static visualizations from the deduplicated data.

### Generated Charts

![OS Distribution](app/visualizations/images/os_distribution.png)

**OS Distribution**: Shows the distribution of operating systems across all hosts (Linux, Windows, macOS)

![Source Distribution](app/visualizations/images/source_distribution.png)

**Source Distribution**: Shows the distribution of hosts by data source (Qualys vs Crowdstrike)

![Host Freshness](app/visualizations/images/host_age_pie.png)

**Host Freshness**: Shows the ratio of old hosts (>30 days) vs recent hosts (≤30 days)

The charts are automatically created in the `app/visualizations/images/` directory when the pipeline runs. 

[![CI](https://github.com/atamaniuc/hosts_etl/actions/workflows/ci.yml/badge.svg)](https://github.com/atamaniuc/hosts_etl/actions/workflows/ci.yml)
