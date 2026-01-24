# meikaku
AI-powered meeting assistant

## Overview

A mobile app that records audio and generates AI assisted summaries and todos.

## Tech Stack
- **Frontend:** React native (expo)
- **Backend:** FastAPI
- **ML** (TBD)

---

## Setup

Run the following command:

```bash
./setup.sh
```

To start the service:

```bash
docker compose up -d
```

To connect to the postgres container:

```bash
docker exec -it postgres-db psql -U meikaku -d meikaku
```
