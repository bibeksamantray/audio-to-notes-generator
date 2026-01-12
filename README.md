# AI-Powered Lecture Voice-to-Notes Generator (Local, Open-Source)

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Local%20DB-brightgreen)](https://www.mongodb.com/)


This project converts lecture audio into **transcripts** and **AI-generated notes** using a fully **local and open-source stack**. No cloud APIs, no subscription fees, 100% offline.

---

## Features

* **Speech-to-Text**: Uses [faster-whisper](https://github.com/guillaumekln/faster-whisper) for high-quality, local transcription.
* **AI Notes Generation**: Local LLM via [Ollama](https://ollama.com/) (default: `phi3`) creates structured lecture notes.
* **Backend**: Built with FastAPI for async and easy-to-use APIs.
* **Local Database**: MongoDB stores lecture metadata, transcripts, and notes.
* **Frontend**: Simple HTML/CSS/JS interface for uploading audio, viewing transcripts, and generating notes.
* **Export**: Export notes in **PDF** or **plain text**.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Setup & Installation](#setup--installation)
4. [Running the Backend](#running-the-backend)
5. [Running the Frontend](#running-the-frontend)
6. [Typical Workflow](#typical-workflow)
7. [Key Technical Choices](#key-technical-choices)

---

## Project Structure

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

## Prerequisites

* **Python 3.10+**
* **MongoDB Community Edition** running locally (default URI: `mongodb://localhost:27017`)
* **Ollama** installed and running locally with a model pulled:

  * Recommended: `phi3` (~2.3GB, good balance of speed & quality)
  * Alternatives: `mistral` (~4GB, higher quality) or `tinyllama` (~637MB, faster)
* Modern web browser for the frontend

---

## Setup & Installation

### 1. Create and activate a virtual environment

```bash
cd s-project
python -m venv .venv
# Windows PowerShell
.venv\Scripts\activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Start MongoDB

#### Option A: Fresh Installation

1. Download MongoDB Community Edition: [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Run the installer → choose **Complete** → install as **service** → optional: install MongoDB Compass
3. MongoDB service should start automatically

#### Option B: Check if MongoDB is running

```powershell
Get-Service -Name "MongoDB" | Select-Object Name, Status
```

#### Option C: Start MongoDB manually (service exists but stopped)

```powershell
Start-Service -Name "MongoDB"
```

#### Option D: Run MongoDB manually (if not a service)

```powershell
cd "C:\Program Files\MongoDB\Server\<version>\bin"
.\mongod.exe --dbpath "C:\data\db"
```

Verify MongoDB:

```powershell
mongosh
```

---

### 4. Ensure Ollama is running with a model

```bash
# Start Ollama server (keep terminal open)
ollama serve

# Pull recommended model
ollama pull phi3
```

> If using a different model, update `backend/app/config.py`:
>
> * `LLM_MODEL_NAME = "<your_model_name>"`

---

## Running the Backend

```bash
uvicorn backend.app.main:app --reload
```

* Backend URL: `http://127.0.0.1:8000`
* API docs: `http://127.0.0.1:8000/docs`

---

## Running the Frontend

* Open `frontend/index.html` directly in a browser
* Or serve with a static server (optional)

> The frontend expects the backend at `http://127.0.0.1:8000`.

---

## Typical Workflow

1. Open the frontend (`index.html`)
2. Fill lecture metadata and upload an audio file **or** record via microphone
3. Frontend sends a `POST /api/lectures` request to FastAPI
4. Backend:

   * Saves audio locally (`data/audio/`)
   * Transcribes it with `faster-whisper`
   * Stores transcript and metadata in MongoDB
5. User selects a lecture to view transcript
6. Click **Generate Notes** → local LLM produces structured notes → stored in MongoDB
7. Export notes as **PDF** or **plain text**

---

## Key Technical Choices

* **FastAPI**: modern, async Python framework with automatic API docs
* **MongoDB**: flexible schema for storing transcripts & notes
* **faster-whisper**: optimized, open-source speech-to-text
* **Local LLM with Ollama**: privacy-first, avoids paid cloud APIs
* **Modular structure**: `services/` for AI logic, `routers/` for HTTP endpoints, `schemas.py` for request/response models
* **Synchronous processing**: simpler design; can extend to async jobs if needed

