# Running Without Docker - Local Development Guide

## Prerequisites

1. **Python 3.11+** 
2. **Node.js 20+**
3. **MongoDB** (we'll install this)

## Step-by-Step Setup

### 1. Install MongoDB (Mac)

```bash
# Install using Homebrew
brew tap mongodb/brew
brew install mongodb-community@6.0

# Start MongoDB
brew services start mongodb-community@6.0

# Verify it's running
mongosh --eval "db.version()"
```

### 2. Setup Backend

```bash
cd misinfo-agentic/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in project root
cd ..
cp .env.example .env
```

**Edit `.env` file** and set:
```env
MONGO_URI=mongodb://localhost:27017/misinfo_db
NEWSAPI_KEY=your_newsapi_key_here
SCHED_RUN_INTERVAL_MIN=10
```

**Run backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Setup Frontend (New Terminal)

```bash
cd misinfo-agentic/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Quick Commands

**Start Backend:**
```bash
cd misinfo-agentic/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Start Frontend (separate terminal):**
```bash
cd misinfo-agentic/frontend
npm run dev
```

## Troubleshooting

**If MongoDB won't start:**
```bash
# Check status
brew services list

# Restart
brew services restart mongodb-community@6.0
```

**If Python version is wrong:**
```bash
# Check version
python3 --version

# Install Python 3.11 if needed
brew install python@3.11
```
