# TrainTrack

A lightweight experiment tracker for machine learning — log, visualize and compare training runs in real-time.

## What it does

TrainTrack provides a REST API to log training experiments and a web dashboard to visualize them. During model training, you send loss and metric values to the API at each step. The frontend dashboard displays live-updating charts, highlights min/max values, and allows multi-run comparison — all organized by project and model.

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, SQLAlchemy (async), Pydantic |
| **Database** | PostgreSQL 15 |
| **Frontend** | HTML, CSS, JavaScript, Chart.js |
| **Infrastructure** | Docker, Docker Compose |

> [!NOTE]
> The frontend was entirely built using **Claude Opus 4** (thinking mode).

## Getting Started

### Run with Docker Compose
To start the server with the api go into the server folder and run the Docker compose
```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port `5432`
- **FastAPI** on port `8000`

The frontend is a static site in the `frontend/` folder — open `frontend/index.html` in your browser.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_DB` | `ml_tracking` | Database name |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@db:5432/ml_tracking` | Connection string |

## API Endpoints

Base URL: `http://localhost:8000`

### Models

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/models/` | Register a new model |
| `GET` | `/models/` | List all models |
| `DELETE` | `/models/{model_id}` | Delete a model by ID |
| `DELETE` | `/models/project/{project_name}` | Delete all models in a project |

**Create a model:**
```bash
curl -X POST http://localhost:8000/models/ \
  -H "Content-Type: application/json" \
  -d '{"name": "ResNet50", "project_name": "Image Classification"}'
```

---

### Training Runs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/runs/` | Create a new run (starts as `running`) |
| `GET` | `/runs/runbymodels/{model_id}` | Get all runs for a model |
| `GET` | `/runs/runbyproject/{project_name}` | Get all runs for a project |
| `DELETE` | `/runs/{run_id}` | Delete run(s) (comma-separated IDs) |
| `PATCH` | `/runs/update_status` | Update run status |

**Create a run:**
```bash
curl -X POST http://localhost:8000/runs/ \
  -H "Content-Type: application/json" \
  -d '{"model_id": "<MODEL_UUID>", "hyperparameters": {"lr": 0.001, "batch_size": 32, "epochs": 50}}'
```

**Mark a run as completed:**
```bash
curl -X PATCH http://localhost:8000/runs/update_status \
  -H "Content-Type: application/json" \
  -d '{"run_id": "<RUN_UUID>", "new_status": "completed"}'
```

Status values: `running`, `completed`, `failed`

---

### Loss

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/loss/` | Log a single loss value |
| `POST` | `/loss/batch` | Log multiple loss values at once |
| `GET` | `/loss/?run_id={id}` | Get losses for a run (optional: `split`, `limit`) |

**Log a loss value:**
```bash
curl -X POST http://localhost:8000/loss/ \
  -H "Content-Type: application/json" \
  -d '{"run_id": "<RUN_UUID>", "step": 1, "split": "train", "value": 2.345}'
```

Split values: `train`, `validation`

---

### Metrics

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/metric/` | Log a single metric value |
| `POST` | `/metric/batch` | Log multiple metric values at once |
| `GET` | `/metric/?run_id={id}` | Get metrics for a run (optional: `split`, `metric_name`, `limit`) |

**Log a metric value:**
```bash
curl -X POST http://localhost:8000/metric/ \
  -H "Content-Type: application/json" \
  -d '{"run_id": "<RUN_UUID>", "step": 1, "split": "validation", "metric_name": "accuracy", "value": 0.87}'
```

Available metrics: `accuracy`, `f1-score`, `recall`, `precision`, `balanced accuracy`, `mse`, `mae`

