# BRAHMO Composition Agent — Architecture

## Overview
The Composition Agent transforms 27 raw candidate nodes from the Rules Engine
into a structured, token-efficient context string that fits within a hard
4,000-token ceiling before injection into the AI system prompt.

## Pipeline

### 1. Token Counter (`token_counter.py`)
Uses tiktoken with `cl100k_base` encoding (Claude-compatible).
Counts ALL THREE sources before any API call:
- System prompt (~800 tokens reserved)
- Context string (variable — what we're composing)
- User message estimate (200 tokens reserved)
Total must be under TOKEN_BUDGET (default 4,000).

### 2. Importance Scorer (`importance_scorer.py`)
Each node has two weights from the database:
- `retrieval_weight`: set by Rules Engine — how important for recall
- `injection_weight`: set by Composition Agent — how much token space it deserves
A composite score = (retrieval + injection) / 2 is used for sorting within blocks.

### 3. Block Assembler (`block_assembler.py`)
Nodes are sorted into 8 blocks in LOCKED order:
- Block 1: Role Frame (auto-generated)
- Block 2: Zone 2 Global CONSTRAINTs (always FULL)
- Block 3: Recent DECISIONs (sorted by injection weight)
- Block 4: Zone 1 Department CONSTRAINTs (always FULL)
- Block 5: Session Context (FACTs, ANTI_PATTERNs, remaining DECISIONs)
- Block 6: Open Questions (empty in v0.1)
- Block 7: Stale Flags (REVIEW_REQUIRED nodes only — omitted if none)
- Block 8: Session Boundaries (CAPTURE instruction)

### 4. Distance-Weighted Compressor (`compressor.py`)
Initial compression level assigned by distance from entry point:
- Distance 0-1: FULL (~150 tokens)
- Distance 2: COMPRESSED (~50 tokens)
- Distance 3+: CONSTRAINT_ONLY (~20 tokens)
EXCEPTION: CONSTRAINT nodes are ALWAYS FULL regardless of distance.

### 5. Iterative Budget Fitter (`budget_fitter.py`)
Core loop:
WHILE total_tokens > TOKEN_BUDGET:
find lowest injection_weight non-CONSTRAINT node that is not OMIT
compress it one level down (FULL → COMPRESSED → CONSTRAINT_ONLY → OMIT)
recalculate total
IF all non-CONSTRAINTs are OMIT and still over budget:
raise error — do NOT compress CONSTRAINTs
Compression ordering: lowest injection_weight compressed first.
CONSTRAINTs are never touched even if over budget.

### 6. Context Builder (`context_builder.py`)
Concatenates blocks with headers in locked order.
Outputs final context string + per-node metadata JSON for frontend visualization.

## CONSTRAINT Protection
CONSTRAINT nodes are protected at every stage:
- Compressor assigns FULL regardless of distance
- Budget fitter never selects them as compression candidates
- If CONSTRAINTs alone exceed budget, system raises a budget error
  and flags for human override rather than truncating safety-critical info

## Token Budget Edge Cases
- If CONSTRAINTs alone exceed budget: error flagged, human override required
- Block 7 only rendered if REVIEW_REQUIRED nodes exist (no empty block waste)
- All counting happens BEFORE any API call — overspend is impossible

## Stack
- Backend: Python 3.11, FastAPI, tiktoken, Supabase (PostgreSQL)
- Frontend: Next.js, TypeScript, Tailwind CSS
- Database: Supabase free tier (27 candidate nodes)