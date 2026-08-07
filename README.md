# 🐅 WildTN-News — Tamil Nadu Wildlife & Conservation Intelligence Platform

**WildTN-News** is a fullstack AI-powered news intelligence platform dedicated to aggregating, analyzing, and reporting wildlife news, human-animal conflict alerts, anti-poaching operations, and forest department bulletins across Tamil Nadu (Mudumalai, Anamalai, Sathyamangalam, Coimbatore, Nilgiris, KMTR, Kanyakumari, Megamalai, and Kodaikanal).

---

## 🌟 Key Features

1. **Continuous Automated News Aggregation**:
   - Web scrapers & RSS feed collectors targeting Tamil & English environmental portals.
   - Automatic 15-minute periodic scanning via `APScheduler`.

2. **AI News Classification & Severity Scoring**:
   - Categorization: *Human-Wildlife Conflict, Rescue & Rehabilitation, Forest Dept & Policy, Species Conservation, Anti-Poaching & Crime, Eco-Tourism & Sanctuaries*.
   - Conflict Level Scoring: **HIGH**, **MEDIUM**, **LOW**, **NONE**.
   - Spatial district recognition & target species extraction (Elephants, Tigers, Leopards, Gaur, Nilgiri Tahr, Sea Turtles).

3. **Bilingual Support (English & தமிழ்)**:
   - Instant toggle between English and Tamil headlines, content, and executive 3-bullet summaries.

4. **Automated PDF Bulletin Generator**:
   - Compiles executive PDF digests formatted with custom headers, conflict metrics, and bullet points using ReportLab.
   - Archives PDF files with instant download links.

5. **Interactive Intelligence Analytics Dashboard**:
   - Visualizes hotspot districts, high-risk species metrics, and incident trend data.

---

## 📁 Project Architecture

```
WildTN-News/
│
├── frontend/                  # React + Vite Glassmorphic Frontend Application
│   ├── src/
│   │   ├── pages/             # NewsFeed, PDFDigest, AnalyticsDashboard, CollectorJobs
│   │   ├── components/        # Navbar, Sidebar, ArticleCard, ArticleModal, FilterBar
│   │   ├── services/          # API fetch client
│   │   └── App.jsx
│   └── package.json
│
├── backend/                   # FastAPI Backend Application
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & Static routes
│   │   ├── models/            # Pydantic schemas
│   │   ├── routes/            # REST API endpoints (/api/articles, /api/pdf, /api/analytics, /api/collectors)
│   │   ├── services/          # Persistent Storage service
│   │   ├── collectors/        # RSS, Tamil, & English news scrapers
│   │   ├── ai/                # Classifier, Summarizer, Translator
│   │   ├── pdf/               # ReportLab PDF Generator
│   │   └── scheduler/         # APScheduler jobs
│   └── requirements.txt
│
├── pdfs/                      # Generated PDF report storage directory
├── scripts/                   # Utility & Database seed scripts
├── .env
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### Seed Initial Tamil Nadu Wildlife Data:
```bash
python ../scripts/seed_data.py
```

#### Run FastAPI Server:
```bash
uvicorn app.main:app --port 8000 --reload
```
API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 2. Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
```
Open web app at: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Verification & API Endpoints

- `GET /api/articles` — Fetch filtered wildlife articles
- `POST /api/pdf/generate` — Generate custom executive PDF report
- `GET /api/analytics` — Fetch conflict risk analytics & district hotspots
- `POST /api/collectors/trigger` — Trigger immediate news feed scan
