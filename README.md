# Misinformation Detection — Advanced Agentic AI System

🔍 A complete full-stack system for detecting and verifying misinformation using autonomous AI agents, web scraping, fact-checking, and real-time dashboard visualization.

## 🌟 Features

- **Autonomous Agents**: Three independent agents that run on schedule
  - **Fetcher Agent**: Scrapes news from NewsAPI and extracts full article content
  - **Claim Extractor**: Analyzes content to identify verifiable claims using NLP
  - **Verifier Agent**: Cross-checks claims against trusted sources and assigns confidence scores
  
- **Real-time Dashboard**: Beautiful React interface with:
  - Live updates every 15 seconds
  - Glassmorphism design with dark theme
  - Status tracking for claims (true/false/mixture/unverified)
  - Evidence links for each verification
  
- **Scalable Architecture**: 
  - FastAPI backend with async MongoDB
  - APScheduler for agent orchestration
  - Docker Compose for easy deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React)                       │
│              Dashboard with Real-time Updates            │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Fetcher  │→│ Extractor│→│ Verifier │              │
│  │  Agent   │  │  Agent   │  │  Agent   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              MongoDB Database                            │
│   raw_items │ claims │ verifications                    │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Docker Desktop** (recommended) OR
- **Python 3.11+** and **Node.js 20+** for local development
- **API Keys** (optional but recommended):
  - [NewsAPI](https://newsapi.org/) - Free tier available
  - [Google Custom Search](https://developers.google.com/custom-search) - Optional for verification
  - OpenAI/HuggingFace - Optional for advanced LLM features

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone and Setup

```bash
cd misinfo-agentic
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add your API keys:

```env
NEWSAPI_KEY=your_newsapi_key_here
GOOGLE_CSE_API_KEY=your_google_cse_key  # Optional
GOOGLE_CSE_ID=your_cse_id                # Optional
```

### 3. Launch the System

```bash
docker-compose up --build
```

### 4. Access the Dashboard

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## 💻 Local Development (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export MONGO_URI=mongodb://localhost:27017/misinfo_db
export NEWSAPI_KEY=your_key_here

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/items` | GET | Fetched news items |
| `/api/claims` | GET | Extracted claims |
| `/api/verifications` | GET | Verification results |
| `/api/verify/{claim_id}` | POST | Manually trigger verification |

## 🤖 Agent Pipeline

The system runs a continuous pipeline:

1. **Every 10 minutes** (configurable):
   - Fetcher retrieves latest news
   - Claim Extractor processes new items
   - Verifier checks unverified claims

2. **Claim Extraction**:
   - Analyzes article text
   - Identifies sentences with claim keywords
   - Filters for verifiable statements

3. **Verification**:
   - Searches Google CSE for evidence
   - Checks fact-check databases
   - Assigns confidence score (0-100%)
   - Categorizes as: true/false/mixture/unverified

## 🎨 Dashboard Features

- **Stats Overview**: Claims tracked, verifications completed, sources monitored
- **Claims Feed**: Real-time list of extracted claims with status badges
- **Verifications**: Detailed results with confidence scores and evidence links
- **Auto-refresh**: Updates every 15 seconds
- **Responsive Design**: Works on desktop and mobile

## 🔧 Configuration

Edit `.env` to customize:

```env
SCHED_RUN_INTERVAL_MIN=10  # Agent run interval (minutes)
PORT=8000                   # Backend port
```

## 📊 Database Collections

### `raw_items`
Stores fetched articles:
```json
{
  "source": "NewsAPI",
  "url": "https://...",
  "title": "Article title",
  "summary": "Description",
  "fetched_at": "2024-01-01T00:00:00Z",
  "meta": { "full_text": "..." }
}
```

### `claims`
Extracted claims:
```json
{
  "raw_id": "...",
  "text": "Claim text",
  "extracted_at": "2024-01-01T00:00:00Z",
  "status": "unverified"
}
```

### `verifications`
Verification results:
```json
{
  "claim_id": "...",
  "verdict": "false",
  "score": 0.25,
  "evidence": [...],
  "checked_at": "2024-01-01T00:00:00Z"
}
```

## 🚀 Production Deployment

For production:

1. **Use production-grade MongoDB** (MongoDB Atlas)
2. **Set strong JWT_SECRET**
3. **Enable HTTPS** (nginx reverse proxy)
4. **Use production build** for frontend:
   ```bash
   npm run build
   ```
5. **Scale agents** as separate services with message queue (Redis/Kafka)
6. **Add rate limiting** and caching
7. **Monitor with logs** (structured logging, ELK stack)

## 🔮 Future Enhancements

- [ ] Integration with more fact-check APIs (Snopes, PolitiFact)
- [ ] Advanced LLM-based claim extraction (GPT-4, Claude)
- [ ] User authentication and saved preferences
- [ ] Email/webhook alerts for high-confidence misinformation
- [ ] Social media monitoring (Twitter/X, Reddit APIs)
- [ ] Source credibility scoring
- [ ] Multi-language support
- [ ] Graph visualization of claim networks

## 🤝 Contributing

This is a hackathon/education project. Feel free to:
- Add new agents
- Improve claim extraction algorithms
- Enhance verification logic
- Add new data sources

## 📝 License

MIT License - Feel free to use for hackathons, education, or research.

## 🙏 Acknowledgments

- NewsAPI for news aggregation
- FastAPI and React communities
- Transformers/HuggingFace for NLP models

---

**Built with ❤️ for fighting misinformation**
