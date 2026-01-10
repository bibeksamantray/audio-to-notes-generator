# AI-Powered Lecture Voice-to-Notes Generator (Local, Open-Source)

This project converts lecture audio into **transcripts** and **AI-generated notes** using:

- `faster-whisper` (open-source Whisper) for speech-to-text
- A **local LLM** (Phi model via **Ollama**) for notes generation
- **FastAPI** (Python) for the backend API
- **MongoDB Community Edition** for local data storage
- **HTML, CSS, JavaScript (vanilla)** for the frontend

Everything runs **locally** and uses **100% free and open-source tools**.

---

## 1. Project Structure

```text
backend/
  app/
    __init__.py
    main.py
    config.py
    db.py
    models.py
    schemas.py
    utils/
      logging_config.py
    services/
      transcription.py
      notes_generator.py
      export_service.py
    routers/
      lectures.py
frontend/
  index.html
  styles.css
  app.js
data/
  audio/
  exports/
requirements.txt
```

---

## 2. Prerequisites

- **Python** 3.10+ (recommended)
- **MongoDB Community Edition** running locally (default URI: `mongodb://localhost:27017`)
- **Ollama** installed and running locally, with a suitable model pulled:
  - **Recommended**: `ollama pull tinyllama` (~637MB, fastest and lightweight - configured as default)
  - Alternatives: `ollama pull phi` (~1.6GB) or `ollama pull mistral` (~4GB, best quality)
  - See `OLLAMA_TROUBLESHOOTING.md` or `NETWORK_TIMEOUT_FIX.md` if you encounter download errors
- A modern browser (for the frontend).

---

## 3. Setup & Installation

1. **Create and activate a virtual environment (recommended)**

```bash
cd s-project
python -m venv .venv
.venv\Scripts\activate  # on Windows PowerShell
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Install and Start MongoDB Community Edition**

   **Option A: Install MongoDB Community Edition (if not installed)**
   
   1. Download MongoDB Community Edition for Windows:
      - Go to: https://www.mongodb.com/try/download/community
      - Select: Windows, MSI package
      - Click "Download"
   
   2. Run the installer:
      - Choose "Complete" installation
      - **Important**: Check "Install MongoDB as a Service"
      - Service name: `MongoDB`
      - Run service as: Network Service user
      - Install MongoDB Compass (optional GUI tool)
   
   3. After installation, MongoDB service should start automatically.
   
   **Option B: Check if MongoDB is already running**
   
   Open PowerShell and run:
   ```powershell
   Get-Service -Name "MongoDB" | Select-Object Name, Status
   ```
   
   If Status is "Running", MongoDB is ready!
   
   **Option C: Start MongoDB manually (if service exists but stopped)**
   
   ```powershell
   # Start MongoDB service
   Start-Service -Name "MongoDB"
   
   # Or using net command
   net start MongoDB
   ```
   
   **Option D: Run MongoDB manually (if not installed as service)**
   
   If you installed MongoDB but not as a service, you can run it manually:
   ```powershell
   # Navigate to MongoDB bin folder (usually C:\Program Files\MongoDB\Server\<version>\bin)
   cd "C:\Program Files\MongoDB\Server\7.0\bin"
   
   # Start MongoDB
   .\mongod.exe --dbpath "C:\data\db"
   ```
   
   **Verify MongoDB is running:**
   
   ```powershell
   # Test connection
   mongosh
   # Or if mongosh is not available:
   mongo
   ```
   
   If you see a MongoDB shell prompt, MongoDB is running correctly on `mongodb://localhost:27017`.

4. **Ensure Ollama is running with a model**

```bash
# Start Ollama server (keep this terminal open)
ollama serve

# In another terminal, pull a model (recommended: tinyllama for fastest download)
ollama pull tinyllama
```

**Note:** If you get network timeout errors, try:
- `ollama pull tinyllama` (smallest, ~637MB) - **Recommended for student laptops** (configured as default)
- `ollama pull phi` (smaller, ~1.6GB)
- See `OLLAMA_TROUBLESHOOTING.md` or `NETWORK_TIMEOUT_FIX.md` for detailed help

If you use a different model name, update `backend/app/config.py`:
- `LLM_MODEL_NAME` (default is `"tinyllama"`)

---

## 4. Running the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

This starts FastAPI at `http://127.0.0.1:8000`.

- API docs: `http://127.0.0.1:8000/docs`

---

## 5. Running the Frontend

Simplest approach during development:

- Open `frontend/index.html` directly in the browser (double-click or "Open in Browser").

Or serve it with a simple static server (optional).

The frontend expects the backend at `http://127.0.0.1:8000`.

---

## 6. Typical Workflow

1. User opens the frontend (`frontend/index.html`).
2. User fills lecture metadata and:
   - uploads an audio file **or**
   - records via microphone.
3. Frontend sends a `POST /api/lectures` request (multipart) to FastAPI.
4. Backend:
   - Saves audio locally under `data/audio/`.
   - Transcribes it with `faster-whisper`.
   - Stores transcript and metadata in MongoDB.
5. User selects a lecture from the list to view transcript.
6. User clicks **Generate Notes**:
   - Backend calls local LLM (Ollama) with a structured prompt.
   - Stores generated notes in MongoDB.
7. User can **export notes** as **PDF** or **plain text**.

---

## 7. Key Technical Choices (for Viva)

- **FastAPI**: modern, async Python framework, easy to document and test.
- **MongoDB**: flexible schema for large transcripts and notes text; easy to run locally.
- **faster-whisper**: optimized open-source implementation of Whisper; good for laptops.
- **Local LLM with Ollama**: respects data privacy and avoids paid cloud APIs.
- **Clean modular structure**:
  - `services/` for AI and export logic.
  - `routers/` for HTTP endpoints.
  - `schemas.py` for request/response models.
- **Synchronous transcription and notes generation**:
  - Simpler to implement and explain for a final-year project.
  - Still clear where to extend for background jobs or queues.

