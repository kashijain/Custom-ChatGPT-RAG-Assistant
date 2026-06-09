# 🚀 Render Deployment Guide

This guide describes how to deploy the **Custom ChatGPT RAG Assistant** (both React + Vite frontend and FastAPI backend) on **Render** using either **Blueprints (render.yaml)** or **Manual Setup**.

---

## 🛠️ Environment Variables

### 🎨 Frontend (Static Site)
Configure these variables in your frontend settings under **Environment**:
*   `VITE_API_URL`: The public URL of your backend FastAPI service (e.g., `https://your-backend-name.onrender.com`).
    *   *Note*: Do not include a trailing slash.

### ⚙️ Backend (Web Service)
Configure these variables in your backend settings under **Environment**:
*   `OPENAI_API_KEY`: Your OpenAI API key. If not provided or invalid, the backend automatically falls back to **demo mode** (using local deterministic embeddings and pre-defined text snippets).
*   `OPENAI_EMBEDDING_MODEL`: The model used for embeddings (default: `text-embedding-3-small`).
*   `FALLBACK_EMBEDDING_DIM`: Dimension for local fallback mode if OpenAI key is missing (default: `1536`).
*   `FRONTEND_URL`: The URL of your deployed frontend static site (e.g., `https://your-frontend-name.onrender.com`). Used to allow CORS requests.
*   `CORS_ORIGINS`: Comma-separated list of allowed origins (e.g., `https://your-frontend-name.onrender.com,http://localhost:5173`).

---

## 🚀 Option 1: Automatic Deployment (Render Blueprints)

A `render.yaml` blueprint configuration has been pre-configured in the project root. This file enables automatic deployment of both services in a single step.

### Steps:
1.  Push the updated code to your GitHub / GitLab repository.
2.  Log in to your **Render Dashboard** and click **New > Blueprint**.
3.  Connect the repository containing this project.
4.  Render will parse the `render.yaml` file. You will be prompted to enter the missing secrets (specifically `OPENAI_API_KEY`).
5.  Set your placeholders:
    *   Set the backend's `FRONTEND_URL` to your frontend's expected URL.
    *   Set the frontend's `VITE_API_URL` to your backend's expected URL.
6.  Click **Apply**. Render will automatically orchestrate and build both services!

---

## 🔧 Option 2: Manual Deployment

If you prefer to configure the services manually in the Render Dashboard, follow these steps:

### 1. Backend Web Service
*   **Service Type**: Web Service
*   **Name**: `custom-chatgpt-backend`
*   **Runtime**: `Python`
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
*   **Root Directory**: `backend`
*   **Environment Variables**:
    *   `OPENAI_API_KEY` (Secret)
    *   `OPENAI_EMBEDDING_MODEL` = `text-embedding-3-small`
    *   `FALLBACK_EMBEDDING_DIM` = `1536`
    *   `FRONTEND_URL` = `https://your-frontend-name.onrender.com`
    *   `CORS_ORIGINS` = `https://your-frontend-name.onrender.com`

### 2. Frontend Static Site
*   **Service Type**: Static Site
*   **Name**: `custom-chatgpt-frontend`
*   **Build Command**: `npm install && npm run build`
*   **Publish Directory**: `dist`
*   **Root Directory**: `frontend`
*   **Environment Variables**:
    *   `VITE_API_URL` = `https://your-backend-name.onrender.com`

---

## 🔍 Verification & Testing

Once both services are successfully deployed, perform these checks to verify the system is fully functional:

1.  **Frontend URL Configuration**:
    *   Open your browser's developer console (F12) and inspect the **Network** tab.
    *   Ensure all API requests go to `https://your-backend-name.onrender.com/api/upload` and `https://your-backend-name.onrender.com/api/chat` instead of `localhost`.
2.  **PDF Upload Check**:
    *   Upload a PDF using the frontend file uploader.
    *   Confirm the file processes correctly and reports the number of text chunks indexed.
3.  **FAISS & Chat Integration**:
    *   Ask a question related to the uploaded PDF contents.
    *   Verify the response is generated with grounded source cards displayed below the chat bubble.
4.  **OpenAI Status**:
    *   If `OPENAI_API_KEY` is configured and active, responses will be generated via GPT.
    *   If the key is missing or quota is depleted, the interface will automatically display a notice indicating "Demo mode active" and use local embeddings to match search queries.

---

## 🩺 Troubleshooting Guide

### ❌ Problem: CORS Errors (Blocked by CORS Policy)
*   **Symptoms**: Chat or upload fails, and the browser console displays a CORS block error.
*   **Fix**:
    1. Check your backend `FRONTEND_URL` and `CORS_ORIGINS` environment variables.
    2. Ensure they EXACTLY match your frontend's Render URL (including `https://` and without a trailing slash `/`).
    3. Restart/redeploy the backend web service after updating environment variables.

### ❌ Problem: Vite Frontend Cannot Reach Backend
*   **Symptoms**: UI shows "Unable to reach the backend at..." network error.
*   **Fix**:
    1. Confirm that your backend service is active and running on Render.
    2. Check the frontend's `VITE_API_URL` variable in the Render environment settings. Ensure it points to the correct backend domain.
    3. Remember that **Vite embeds env variables at build time**. If you change `VITE_API_URL`, you **must** trigger a new deploy/build of the frontend static site so the client bundle compiles the new value.

### ❌ Problem: "OpenAI quota is unavailable, so the app is running in demo mode."
*   **Symptoms**: Responses show a demo mode banner, and answer quality is low.
*   **Fix**:
    1. Verify `OPENAI_API_KEY` is set correctly in the Render backend environment variables.
    2. If set, check if your OpenAI account has remaining credits/quota on their dashboard.
    3. The application is designed to degrade gracefully (using SHA-256 deterministic fallback embeddings) so it remains testable even without an active OpenAI subscription.
