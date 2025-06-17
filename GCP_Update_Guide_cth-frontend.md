## Clinical Trials Hub – Frontend Cloud Run Deployment Guide

This document outlines a repeatable process for building and deploying the React frontend to Google Cloud Run.

**Any fields that require updates during future deployments are marked clearly as 🔧.**

---

## Overview: Deployment Flow

1. Build the React app locally for production
2. Package it as a Docker image
3. Push the image to Google Container Registry (GCR)
4. Deploy the image to Cloud Run

---

## Step 1: Build the React App Locally

```bash
git pull origin develop
npm install            # or yarn
npm run build          # builds using .env.production
```

🔧 **Make sure that:**

* `REACT_APP_API_URL` in `.env.production` is up to date
  Example:

  ```
  REACT_APP_API_URL=https://cth-backend-103266204202.us-central1.run.app
  ```

---

## Step 2: Build and Push the Docker Image

```bash
docker buildx build \
  --platform=linux/amd64 \
  -t gcr.io/cth-docker-hosting/cth-frontend:🔧v2 \
  --push .
```

🔧 **Update the image tag (`:v2`) for each deployment.**
Suggested formats: `:v3`, `:latest`, `:20240616`, etc.

---

## Step 3: Deploy to Cloud Run

```bash
gcloud run deploy cth-frontend \
  --image=gcr.io/cth-docker-hosting/cth-frontend:🔧v2 \
  --project=cth-docker-hosting \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated
```

🔧 **Make sure the tag here matches the one used in Step 2.**

---

## .env.production Example

```env
REACT_APP_API_URL=https://cth-backend-🔧103266204202.us-central1.run.app
```

🔧 **If the backend URL changes**, update this value and rebuild with `npm run build`.

---

## Deployed URL

```
https://cth-frontend-103266204202.us-central1.run.app
```

You can update DNS to point to this address if needed.

---

## 📌 Notes & Recommendations

* The existing `Dockerfile` typically does not need modification
* No custom `nginx.conf` is required unless you're adding advanced routing
* For simplicity, you may use `:latest` as the Docker tag, but versioning is preferred in production

---

Let me know if you’d like a `.env.production` or `Dockerfile` template included. This guide is ready for reuse in future deployments.
