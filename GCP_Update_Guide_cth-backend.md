## Objective

* Migrate a local PostgreSQL database (`trials`) to Google Cloud SQL (PostgreSQL 17).
* Deploy a FastAPI backend to Cloud Run and connect it to the migrated database.

---

## Step 1: Export Local PostgreSQL Database

```bash
pg_dump -U jiwoo -d trials -f ~/Downloads/trials_dump.sql
```

* Use SQL format for compatibility with Cloud SQL imports.
* You may restrict the export to a specific schema using flags like `-n ctgov`.

---

## Step 2: Create a Cloud SQL Instance

```bash
gcloud sql instances create trials-db \
  --database-version=POSTGRES_17 \
  --tier=db-perf-optimized-N-2 \
  --region=us-central1
```

Note: For lower-cost options, consider `--tier=db-f1-micro` or `db-custom-1-3840`.

---

## Step 3: Create Database and User

```bash
gcloud sql databases create trials --instance=trials-db
gcloud sql users create jiwoo --instance=trials-db --password=Psql9980@@
```

Update the password and store it securely.

---

## Step 4: Import the Dump File to Cloud SQL

### 4.1 Create a Cloud Storage Bucket (one-time setup)

```bash
gcloud storage buckets create gs://trials-sql-import --location=us-central1
```

---

### 4.2 Upload the Dump File

```bash
gsutil cp ~/Downloads/trials_dump.sql gs://trials-sql-import/trials_ctgov_dump.sql
```

---

### 4.3 Import the SQL File into Cloud SQL

```bash
gcloud sql import sql trials-db \
  gs://trials-sql-import/trials_ctgov_dump.sql \
  --database=trials \
  --user=jiwoo
```

If you receive an error like:

```
HTTPError 409: Operation failed because another operation was already in progress.
```

Check running operations:

```bash
gcloud sql operations list --instance=trials-db
```

---

## Step 5: Configure Environment Variables for Cloud Run

Create an `env.cloud.yaml` file containing:

```yaml
DB_HOST: "/cloudsql/cth-docker-hosting:us-central1:trials-db"
DB_PORT: "5432"
DB_NAME: "trials"
DB_USER: "jiwoo"
DB_PASS: "Psql9980@@"

AZURE_OPENAI_ENDPOINT: "..."
AZURE_OPENAI_API_KEY: "..."
AZURE_OPENAI_API_VERSION: "..."

CORS_ORIGINS: "http://localhost:3000,..."
NCBI_API_KEY: "..."
ADMIN_EMAIL: "jiwoopark3620@gmail.com"
```

Update API keys and credentials as appropriate.

---

## Step 6: Build and Deploy FastAPI Backend to Cloud Run

### 6.1 Dockerfile Example

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers"]
```

---

### 6.2 Build the Docker Image (Apple Silicon: use amd64)

```bash
docker buildx build --platform=linux/amd64 \
  -t gcr.io/cth-docker-hosting/cth-backend:v2 \
  --push .
```

---

### 6.3 Deploy to Cloud Run

```bash
gcloud run deploy cth-backend \
  --image=gcr.io/cth-docker-hosting/cth-backend:v2 \
  --project=cth-docker-hosting \
  --region=us-central1 \
  --add-cloudsql-instances=cth-docker-hosting:us-central1:trials-db \
  --env-vars-file=env.cloud.yaml
```

---

## Step 7: Database Configuration in FastAPI

Inside your application, configure the database connection using environment variables:

```python
from sqlalchemy import create_engine
import os

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
```

This ensures your FastAPI application connects to the correct Cloud SQL instance at runtime.

---

## Troubleshooting Reference

| Symptom                                           | Resolution                                        |
| ------------------------------------------------- | ------------------------------------------------- |
| `ModuleNotFoundError: No module named 'psycopg2'` | Add `psycopg2-binary` to `requirements.txt`       |
| `ModuleNotFoundError: No module named 'aiohttp'`  | Add `aiohttp` to `requirements.txt`               |
| Cloud Run image error: `must support amd64/linux` | Ensure Docker build uses `--platform=linux/amd64` |
| Docker build fails with `pg_config not found`     | Use `psycopg2-binary` instead of `psycopg2`       |

---

## Checklist for Reuse and Maintenance

| Item                       | Notes                                                      |
| -------------------------- | ---------------------------------------------------------- |
| `trials_dump.sql`          | Re-export whenever database content is updated             |
| `DB_PASS`                  | Update in both Cloud SQL and `env.cloud.yaml` if rotated   |
| Docker image tag (`v2`)    | Use versioned tags (`v3`, `v4`, etc.) to track deployments |
| Frontend `.env.production` | Rebuild frontend if API base URL changes                   |

---
