# BRAHMO Composition Agent

Token Budget + 8-Block Assembly + Iterative Compression

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account (free tier)

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn supabase python-dotenv tiktoken

cp .env.example .env
# Fill in SUPABASE_URL and SUPABASE_KEY
```

Run schema SQL then seed SQL from `supabase/` folder in Supabase SQL Editor.

```bash
uvicorn backend.main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Usage

1. Select user (Dr. Vikram or Nurse Priya)
2. Select patient (Mr. Rajan or Mrs. Padma)
3. Adjust token budget slider (default 4000)
4. Click Compose Context
5. View token breakdown, compression log, 8-block structure, per-node details

## Architecture

See `docs/architecture.md`

## Key Design Decisions

- Token counting uses tiktoken `cl100k_base` — same encoding as Claude
- ALL THREE token sources counted before any API call
- CONSTRAINT nodes never compressed under any circumstances
- Iterative compression targets lowest injection_weight nodes first
- Block 7 only rendered when REVIEW_REQUIRED nodes exist