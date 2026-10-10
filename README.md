# ⚡ NEXORA AI — Knowledge & Productivity Copilot

> A production-grade AI Engineering project built with FastAPI, React, Ollama, RAG, and ChromaDB.

![NEXORA AI](https://img.shields.io/badge/NEXORA-AI%20Copilot-6366f1?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)

---

## 🎯 Project Overview

NEXORA AI is a full-stack AI-powered knowledge and productivity platform that demonstrates:

- **RAG Architecture** — Ask questions from your PDF documents
- **Local LLM Integration** — Runs on your laptop using Ollama (TinyLlama/Phi3)
- **Multi-Agent AI** — Tutor, Planner, and Memory agents
- **Voice AI** — Speech-to-Text and Text-to-Speech
- **Modern Full-Stack** — FastAPI backend + React TypeScript frontend
- **Production-Grade** — JWT auth, PostgreSQL, ChromaDB, analytics

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Chat | Real-time chat with memory & multi-agent support |
| 📄 RAG System | Upload PDFs → Ask questions → Get cited answers |
| 🎙️ Voice AI | Browser-based STT + gTTS for TTS |
| 🧠 Multi-Agent | Tutor Agent, Planner Agent, Memory Agent |
| 📊 Dashboard | KPI cards, activity charts, agent usage stats |
| 🔐 Auth | JWT-based login & registration |
| 🗄️ PostgreSQL | Production-grade relational database |
| 🔍 ChromaDB | Vector store for semantic search |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              NEXORA AI System               │
├──────────────┬──────────────────────────────┤
│   Frontend   │         Backend              │
│  React + TS  │  FastAPI + Python            │
│  TailwindCSS │                              │
│  Zustand     │  ┌─────────┐  ┌──────────┐  │
│  Recharts    │  │PostgreSQL│  │ ChromaDB │  │
│  Framer      │  └─────────┘  └──────────┘  │
│  Motion      │                              │
│              │  ┌─────────────────────────┐ │
│              │  │      Ollama LLM         │ │
│              │  │  TinyLlama / Phi3-mini  │ │
│              │  └─────────────────────────┘ │
└──────────────┴──────────────────────────────┘
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Ollama ([ollama.com](https://ollama.com))

### Step 1 — Clone & Setup Backend

```bash
cd NEXORA_AI/backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2 — Setup PostgreSQL

```sql
CREATE USER nexora_user WITH PASSWORD 'nexora_pass';
CREATE DATABASE nexora_db;
GRANT ALL PRIVILEGES ON DATABASE nexora_db TO nexora_user;
```

### Step 3 — Configure Environment

```bash
cp .env .env.local
# Edit .env with your PostgreSQL credentials
```

### Step 4 — Setup Ollama

```bash
ollama serve
ollama pull tinyllama
```

### Step 5 — Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Step 6 — Setup & Run Frontend

```bash
cd frontend
npm install
npm run dev
```

### Step 7 — Open Browser

```
Frontend:  http://localhost:5173
API Docs:  http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login & get JWT token |
| GET  | `/api/auth/me` | Get current user |
| POST | `/api/ai/chat` | Send message to AI |
| GET  | `/api/ai/chats` | Get all chat sessions |
| POST | `/api/ai/chat/stream` | Streaming AI response |
| POST | `/api/rag/upload` | Upload PDF document |
| POST | `/api/rag/query` | Ask question from docs |
| GET  | `/api/rag/documents` | List uploaded documents |
| POST | `/api/voice/speech-to-text` | Convert audio to text |
| POST | `/api/voice/text-to-speech` | Convert text to audio |
| GET  | `/api/analytics/dashboard` | Get dashboard stats |
| GET  | `/health` | System health check |

---

## 🤖 AI Agents

### General Agent
Default conversational AI with memory support.

### Tutor Agent
Educational assistant that explains topics step-by-step with examples.
```
Input: "Explain RAG architecture"
Output: Structured explanation with overview, concepts, examples, and next steps
```

### Planner Agent
Productivity assistant that creates actionable plans from goals.
```
Input: "Plan my AI Engineering final project"
Output: Phased project plan with timelines and success metrics
```

---

## 📁 Project Structure

```
NEXORA_AI/
├── backend/
│   ├── app/
│   │   ├── ai/          # LLM, RAG, Agents, Prompts, Voice
│   │   ├── api/         # FastAPI route handlers
│   │   ├── core/        # Config, Security, Logger
│   │   ├── database/    # PostgreSQL + ChromaDB setup
│   │   ├── models/      # SQLAlchemy ORM models
│   │   └── main.py      # App entry point
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── api/         # Axios API clients
        ├── components/  # Reusable UI components
        ├── pages/       # Route pages
        └── store/       # Zustand state management
```

---

## 🔮 Future Improvements

- [ ] Docker containerization
- [ ] Multi-user document sharing
- [ ] Streaming chat with SSE
- [ ] Fine-tuned domain-specific models
- [ ] Mobile app (React Native)
- [ ] Stripe payment integration (SaaS)
- [ ] Multi-language support (Bengali NLP)
- [ ] Export chat history as PDF

---

## 📜 License

MIT License — Free to use for educational and commercial purposes.

---

## 👨‍💻 Built For

**Professional AI Engineering Final Examination Project**
Demonstrating: RAG · Local LLM · Prompt Engineering · Multi-Agent AI · Full-Stack Architecture
