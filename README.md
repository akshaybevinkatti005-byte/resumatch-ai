# ResuMatch AI

> Zero-cost, API-free resume optimization & job matching platform powered by local NLP models.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## Features

- **ATS Ghost Score** — Rule-based scoring across 4 dimensions (Parsing, Keywords, Formatting, Structure)
- **Skill DNA Heatmap** — Treemap visualization: area = market demand, color = your proficiency
- **Semantic Job Matching** — ONNX-powered cosine similarity against 50+ job board listings
- **Career Trajectory** — ESCO-inspired next-role recommendations with skill gap analysis
- **100% Local** — No API keys, no data leaves your device, runs on free-tier hosting

## Architecture

```
Frontend (React 18 + Vite)  →  Backend (FastAPI)  →  Local NLP Models
     ↓                              ↓                      ↓
  Tailwind CSS              PyMuPDF + spaCy         ONNX Runtime
  Framer Motion             Rule Engine             all-MiniLM-L6-v2 (INT8)
  Recharts                  Job Aggregator          ~23MB quantized model
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# (Optional) Generate ONNX model for semantic matching
# Requires: pip install optimum[onnxruntime] torch transformers
python quantize_model.py

# Start server
python main.py
```

The backend runs at `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend runs at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check & model status |
| `POST` | `/analyze-resume` | Upload PDF, returns full analysis |
| `GET` | `/jobs` | Aggregated job listings (cached 30min) |

### POST /analyze-resume

```bash
curl -X POST http://localhost:8000/analyze-resume \
  -F "file=@resume.pdf" \
  -F "target_keywords=React,TypeScript,Node.js"
```

## ATS Ghost Score Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Parsing Accuracy | 35% | Text clarity, single-column check |
| Keyword Coverage | 30% | Skill placement multiplier scoring |
| Formatting | 20% | No images/tables/emojis check |
| Structure | 15% | Contact info + standard sections |

## Memory Optimization

Designed for 512MB RAM (Render free tier):
- **ONNX INT8 quantized model** (~23MB vs 90MB FP32)
- **`tokenizers` library** instead of full `transformers` (~20MB vs ~500MB)
- **No PyTorch in production** — only needed for one-time quantization
- **Lazy model loading** with explicit cleanup after each request
- **Single worker** to prevent memory duplication

## Job Sources

Aggregates from 4 unauthenticated public APIs:
- [RemoteOK](https://remoteok.com/api)
- [Jobicy](https://jobicy.com/api/v2/remote-jobs)
- [Arbeitnow](https://www.arbeitnow.com/api/job-board-api)
- [Himalayas](https://himalayas.app/jobs/api)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.10+ |
| PDF Parsing | PyMuPDF (fitz) |
| NER | spaCy (en_core_web_sm) |
| Embeddings | ONNX Runtime + all-MiniLM-L6-v2 |
| Frontend | React 18, TypeScript, Vite |
| Styling | Tailwind CSS 3 |
| Animations | Framer Motion |
| Charts | Recharts |
| HTTP | httpx (async), axios |

## License

MIT
