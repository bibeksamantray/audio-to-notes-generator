<div align="center">

# 🎙️ AI-Powered Lecture Voice-to-Notes Generator

### Transform audio lectures into structured, study-ready notes using 100% local AI

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)

</div>

---

## 📖 Overview

A fully **local, open-source, and privacy-focused** solution that converts lecture audio into high-quality transcripts and AI-generated study notes. No cloud APIs, no subscriptions, no data leaves your machine.

Perfect for students, educators, and lifelong learners who want to:
- 📝 Convert lecture recordings into searchable text
- 🤖 Generate structured, exam-ready notes automatically
- 🔒 Keep all data private and offline
- 💰 Avoid expensive cloud API costs

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎤 **Audio Transcription** | High-quality speech-to-text using [faster-whisper](https://github.com/guillaumekln/faster-whisper) |
| 🤖 **AI Note Generation** | Structured notes via local LLM ([Ollama](https://ollama.com/)) - Mistral 7B |
| 🌐 **Multilingual Support** | Detects and transcribes ~100 languages automatically |
| 📱 **Microphone Recording** | Record lectures directly in the browser |
| 💾 **Local Storage** | All data stored locally in MongoDB |
| 📄 **Export Options** | Export notes as PDF or plain text |
| ⚡ **Fast & Async** | Built with FastAPI for high performance |
| 🎨 **Modern UI** | Clean, responsive web interface |
| 🗑️ **Lecture Management** | Easy delete and organize your lectures |

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **MongoDB Community Edition** ([Download](https://www.mongodb.com/try/download/community))
- **Ollama** ([Download](https://ollama.com/download))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/audio-to-notes-generator.git
   cd audio-to-notes-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start MongoDB**
   ```bash
   # Windows (if installed as service)
   Get-Service -Name "MongoDB" | Start-Service
   
   # Or check if already running
   Get-Service -Name "MongoDB" | Select-Object Name, Status
   ```

5. **Start Ollama and pull model**
   ```bash
   # Terminal 1: Start Ollama server
   ollama serve
   
   # Terminal 2: Pull Mistral model (recommended)
   ollama pull mistral:7b
   ```

6. **Start the backend**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   
   Backend will run at: `http://127.0.0.1:8000`
   
   API Docs: `http://127.0.0.1:8000/docs`

7. **Open the frontend**
   
   Simply open `frontend/index.html` in your web browser

---

## 📁 Project Structure

```
audio-to-notes-generator/
├── backend/
│   └── app/
│       ├── routers/          # API endpoints
│       │   └── lectures.py
│       ├── services/         # Core business logic
│       │   ├── transcription.py
│       │   ├── notes_generator.py
│       │   └── export_service.py
│       ├── utils/            # Utilities
│       │   └── logging_config.py
│       ├── main.py          # FastAPI app entry
│       ├── config.py        # Configuration
│       ├── db.py            # MongoDB connection
│       ├── models.py        # Data models
│       └── schemas.py       # Pydantic schemas
├── frontend/
│   ├── index.html          # Main UI
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
├── data/
│   ├── audio/              # Uploaded audio files
│   └── exports/            # Exported notes
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🎯 Usage

### Basic Workflow

1. **Upload or Record**
   - Fill in lecture metadata (title, course, lecturer, date)
   - Upload an audio file OR record directly via microphone

2. **Automatic Transcription**
   - Backend transcribes audio using faster-whisper
   - Transcript appears in the UI automatically

3. **Generate Notes**
   - Click "Generate Notes" button
   - Local LLM (Mistral 7B) creates structured study notes
   - Notes appear with proper formatting

4. **Export & Study**
   - Export notes as PDF or plain text
   - Use for exam preparation and revision

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/lectures` | List all lectures |
| `POST` | `/api/lectures` | Upload and transcribe audio |
| `GET` | `/api/lectures/{id}` | Get lecture details |
| `POST` | `/api/lectures/{id}/generate-notes` | Generate AI notes |
| `GET` | `/api/lectures/{id}/export` | Export notes (PDF/TXT) |
| `DELETE` | `/api/lectures/{id}` | Delete lecture |

Full API documentation: `http://127.0.0.1:8000/docs`

---

## ⚙️ Configuration

Edit `backend/app/config.py` to customize:

```python
# MongoDB settings
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB_NAME = "lecture_notes_db"

# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE = "small"

# LLM settings
LLM_BACKEND = "ollama"
LLM_MODEL_NAME = "mistral:7b"  # or "phi3", "llama3.2", etc.
LLM_API_BASE_URL = "http://localhost:11434"
```

### Recommended Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `mistral:7b` | 4.4 GB | Medium | ⭐⭐⭐⭐⭐ | **Recommended** - Best quality notes |
| `phi3` | 2.3 GB | Fast | ⭐⭐⭐⭐ | Good balance |
| `llama3.2` | 2 GB | Fast | ⭐⭐⭐ | Quick processing |
| `tinyllama` | 637 MB | Very Fast | ⭐⭐ | Low-resource systems |

---

## 🔧 Troubleshooting

### Common Issues

**MongoDB connection error**
```bash
# Verify MongoDB is running
mongosh

# If not running, start it
Start-Service -Name "MongoDB"  # Windows
sudo systemctl start mongod    # Linux
```

**Ollama model not found**
```bash
# Check installed models
ollama list

# Pull required model
ollama pull mistral:7b
```

**Backend port already in use**
```bash
# Use different port
uvicorn backend.app.main:app --reload --port 8001
```

**HuggingFace symlinks warning (Windows)**
- Non-critical warning
- To fix: Enable Developer Mode in Windows Settings
- Or: Run as administrator

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Database**: MongoDB (Motor async driver)
- **AI/ML**: 
  - [faster-whisper](https://github.com/guillaumekln/faster-whisper) (speech-to-text)
  - [Ollama](https://ollama.com/) (local LLM inference)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Export**: ReportLab (PDF generation)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Report bugs** - Open an issue with details
2. 💡 **Suggest features** - Share your ideas
3. 🔧 **Submit PRs** - Fix bugs or add features
4. 📖 **Improve docs** - Help make the docs better

### Development Setup

```bash
# Fork and clone the repo
git clone https://github.com/yourusername/audio-to-notes-generator.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git commit -m "Add: your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Efficient speech recognition
- [Ollama](https://ollama.com/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python framework
- [MongoDB](https://www.mongodb.com/) - Flexible NoSQL database

---
