# SETUP GUIDE: Token Budget + Iterative Compression
## Composition Agent: Environment Setup + 28 Candidate Nodes + 8-Block Template

---

## ENVIRONMENT SETUP

### What You Need Installed

| Tool | Why |
|------|-----|
| Python (3.11+) OR Node.js (v18+) | Runtime |
| Git | Version control |
| VS Code (recommended) | Code editor |
| Supabase account (free) | PostgreSQL database |
| Any LLM API key | Chat demo after composition (free tier sufficient) |
| tiktoken (pip install) | Accurate token counting |

### Mac Setup

```bash
brew install python@3.11 node

mkdir brahmo-composition-agent
cd brahmo-composition-agent && git init

# Python backend
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn supabase python-dotenv tiktoken

# React frontend
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --no-import-alias
cd frontend && npm install @supabase/supabase-js

cd ..
cat > .env << 'EOF'
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
LLM_API_KEY=your_key
TOKEN_BUDGET=4000
SYSTEM_PROMPT_RESERVE=800
USER_MESSAGE_RESERVE=200
EOF
```

### Supabase Setup

```
1. supabase.com → Create project: "brahmo-composition"
2. Settings → API → Copy URL + anon key
3. SQL Editor → Run schema SQL below
4. SQL Editor → Run seed data SQL below
5. Verify: SELECT COUNT(*) FROM candidate_nodes → 28
```

---

## AI STARTER PROMPT

```
I'm building a Composition Agent for BRAHMO — a system that transforms
28 raw candidate nodes into a structured, token-efficient context string
that fits within a hard 4,000-token ceiling.

TECH STACK: FastAPI + React + Supabase + tiktoken + Tailwind

CORE MODULES:

1. Token Counter:
   Count tokens using tiktoken with cl100k_base encoding (Claude-compatible).
   Count ALL THREE sources BEFORE any API call:
   - System prompt (~800 tokens)
   - Context string (varies — the thing we're composing)
   - User message estimate (~200 tokens)
   Total must be under TOKEN_BUDGET (default 4,000).
   ANTI-PATTERN: counting ONLY the context string misses 1,000 tokens.

2. Dual Importance Scorer:
   Each node has TWO weights:
   - retrieval_weight (0.0-1.0): set by Rules Engine, measures "should this
     be in the candidate set at all?" Higher = more important for recall.
   - injection_weight (0.0-1.0): set by Composition Agent, measures "how
     much token space should this node get?" Higher = full content, lower = compressed.
   CONSTRAINT: retrieval 0.8-1.0, injection 0.8-1.0 (always full, always included)
   DECISION: retrieval 0.5-0.8, injection 0.4-0.7
   ANTI_PATTERN: retrieval 0.7-0.9, injection 0.5-0.8
   FACT: retrieval 0.3-0.6, injection 0.1-0.4

3. Block Assembler:
   Sort nodes into 8 blocks in FIXED order:
   Block 1: Role Frame (auto-generated from user + org)
   Block 2: Zone 2 Global Constraints (Zone 2 + type CONSTRAINT → ALWAYS FULL)
   Block 3: Recent Decisions (DECISION nodes, sorted by recency)
   Block 4: Active Constraints (Zone 1 CONSTRAINTs — ALWAYS FULL)
   Block 5: Session-Specific Context (FACTs + ANTI_PATTERNs + remaining DECISIONs)
   Block 6: Open Questions (empty in v0.1)
   Block 7: Stale Flags (REVIEW_REQUIRED nodes only — omit block if none)
   Block 8: Session Boundaries (CAPTURE: instruction)
   CRITICAL: Blocks 1-2-3-4-5-6-7-8 order is LOCKED. Never reorder.

4. Distance-Weighted Compressor:
   Assign compression level based on distance from entry point:
   - Distance 0-1: FULL content (~150 tokens)
   - Distance 2: COMPRESSED (~50 tokens — key facts summary)
   - Distance 3+: CONSTRAINT_ONLY (~20 tokens — just the rule)
   EXCEPTION: CONSTRAINT type nodes = ALWAYS FULL regardless of distance.
   Each node has pre-generated content at all 3 levels in the database.

5. Iterative Budget Fitter:
   total = system_prompt_tokens + context_tokens + user_reserve_tokens
   WHILE total > TOKEN_BUDGET:
     - Find the node with LOWEST injection_weight that is NOT a CONSTRAINT
     - Compress it to the next lower level:
       FULL → COMPRESSED → CONSTRAINT_ONLY → OMIT
     - Recalculate total
   If ALL non-CONSTRAINTs are OMITTED and still over → flag error, do NOT
   compress CONSTRAINTs.

6. Context String Builder:
   Concatenate blocks in order with block headers:
   "=== ROLE ===\n{block1}\n=== GLOBAL CONSTRAINTS ===\n{block2}\n..."
   Output: the final context_string + composition_metadata JSON

7. Frontend:
   - User selector (Dr. Vikram, Nurse Priya)
   - Patient selector (Mr. Rajan, Mrs. Padma)
   - [Compose Context] button
   - Token budget bar (3-source visual: system + context + user)
   - 8-block structure panel (per-block token counts, collapsible)
   - Per-node detail cards (type, weights, distance, compression level, block)
   - Iterative compression log (pass-by-pass reduction)
   - Budget slider (change from 4,000 to 2,000, watch composition adapt)
   - Composition rationale: include/exclude reason per node
   - [View Final Context String] modal
```

---

## PROJECT STRUCTURE

```
brahmo-composition-agent/
├── README.md
├── .env / .env.example
├── docs/architecture.md
├── backend/
│   ├── main.py
│   ├── composition/
│   │   ├── token_counter.py       ← tiktoken-based 3-source counting
│   │   ├── importance_scorer.py   ← Dual importance (retrieval + injection)
│   │   ├── block_assembler.py     ← 8-block sorted structure
│   │   ├── compressor.py          ← Distance-weighted + CONSTRAINT protection
│   │   ├── budget_fitter.py       ← Iterative compression loop
│   │   └── context_builder.py     ← Final context string assembly
│   └── models/
│       ├── candidate.py
│       ├── block.py
│       └── composition_result.py
├── frontend/src/
│   ├── app/page.tsx
│   ├── components/
│   │   ├── BudgetBar.tsx          ← 3-source visual bar
│   │   ├── BlockPanel.tsx         ← 8-block structure with token counts
│   │   ├── NodeCard.tsx           ← Per-node detail with weights
│   │   ├── CompressionLog.tsx     ← Pass-by-pass iteration log
│   │   ├── BudgetSlider.tsx       ← Adjustable budget demo
│   │   ├── ContextViewer.tsx      ← Final context string modal
│   │   └── CompositionRationale.tsx
│   └── lib/supabase.ts
└── supabase/
    ├── schema.sql
    └── seed.sql
```

---

## TIME MANAGEMENT (8 hours)

| Phase | Hours | Focus |
|-------|:-----:|-------|
| Setup + read assessment | 0.5 | Environment, Supabase, understand pipeline |
| Schema + seed data (28 nodes) | 0.5 | Load candidates, verify token counts |
| Token counter (3-source) | 1.0 | tiktoken integration, 3-source counting |
| 8-block assembler + compression | 1.5 | MOST CRITICAL — block sorting + distance compression |
| Iterative budget fitter | 1.5 | Compression loop + CONSTRAINT protection |
| Dual importance scoring + visualization | 1.0 | Retrieval vs injection weights visible |
| Frontend (budget bar, block panel, compression log) | 1.5 | Make composition decisions visible |
| Test + innovation | 0.5 | Budget slider, edge cases |

---

## DATABASE SCHEMA

```sql
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    config JSONB DEFAULT '{}'
);

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    ceiling_level INTEGER NOT NULL
);

CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    conditions TEXT[]
);

-- The 28 candidate nodes (pre-filtered by Rules Engine)
CREATE TABLE candidate_nodes (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('CONSTRAINT', 'DECISION', 'ANTI_PATTERN', 'FACT')),
    title TEXT NOT NULL,
    content_full TEXT NOT NULL,            -- FULL version (~150 tokens)
    content_compressed TEXT NOT NULL,      -- COMPRESSED version (~50 tokens)
    content_constraint_only TEXT NOT NULL, -- CONSTRAINT_ONLY version (~20 tokens)
    importance DECIMAL(3,2) NOT NULL,
    retrieval_weight DECIMAL(3,2) NOT NULL,
    injection_weight DECIMAL(3,2) NOT NULL,
    distance_from_entry INTEGER NOT NULL,
    zone INTEGER NOT NULL DEFAULT 1,       -- 1=addressed, 2=global
    department TEXT,
    status TEXT DEFAULT 'ACTIVE',
    block_assignment INTEGER,              -- which of the 8 blocks (computed)
    compression_level TEXT DEFAULT 'FULL', -- current compression (computed)
    tokens_full INTEGER,                   -- pre-counted
    tokens_compressed INTEGER,
    tokens_constraint_only INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Composition results (for history/comparison)
CREATE TABLE composition_results (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT NOT NULL,
    patient_id TEXT,
    token_budget INTEGER NOT NULL,
    system_prompt_tokens INTEGER NOT NULL,
    user_reserve_tokens INTEGER NOT NULL,
    context_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    nodes_included INTEGER NOT NULL,
    nodes_omitted INTEGER NOT NULL,
    compression_passes INTEGER NOT NULL,
    constraints_protected INTEGER NOT NULL,
    context_string TEXT NOT NULL,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## SEED DATA — ORGANIZATION + USERS + PATIENTS

```sql
INSERT INTO organizations (id, name, config) VALUES
('supra', 'Supra Multi-Specialty Hospital',
 '{"token_budget": 4000, "system_prompt_reserve": 800, "user_message_reserve": 200}');

INSERT INTO users (id, org_id, name, role, department, ceiling_level) VALUES
('U-VIKRAM', 'supra', 'Dr. Vikram (HOD Ortho)', 'HOD', 'ortho', 4),
('U-PRIYA', 'supra', 'Nurse Priya', 'VIEWER', 'ortho', 10);

INSERT INTO patients (id, org_id, name, age, gender, conditions) VALUES
('PAT-RAJAN', 'supra', 'Mr. Rajan', 68, 'M', '{"Cardiac stent", "AF on Warfarin", "Knee pain OA"}'),
('PAT-PADMA', 'supra', 'Mrs. Padma', 62, 'F', '{"Type 2 DM", "Hypertension", "Fasting observance"}');
```

---

## SEED DATA — 28 CANDIDATE NODES

These are PRE-FILTERED by the Rules Engine. Your Composition Agent receives them as input.

```sql
INSERT INTO candidate_nodes (id, org_id, type, title, content_full, content_compressed, content_constraint_only, importance, retrieval_weight, injection_weight, distance_from_entry, zone, department, tokens_full, tokens_compressed, tokens_constraint_only) VALUES

-- ============================================================
-- ZONE 2 GLOBAL CONSTRAINTS (Block 2 — always FULL)
-- ============================================================

('C-01', 'supra', 'CONSTRAINT', 'Warfarin-NSAID Interaction',
 'CRITICAL: Never prescribe NSAIDs (ibuprofen, aspirin, diclofenac) to patients on Warfarin or other anticoagulants. Risk of life-threatening GI bleed. Alternative: Paracetamol for pain, PPI cover if anti-inflammatory absolutely needed. Supra policy: automatic pharmacy flag on co-prescription.',
 'No NSAIDs with Warfarin — GI bleed risk. Use Paracetamol.',
 'CONSTRAINT: No NSAIDs + Warfarin.',
 0.98, 0.98, 0.95, 4, 2, NULL, 85, 22, 8),

('C-02', 'supra', 'CONSTRAINT', 'Blood Transfusion Two-Person Verification',
 'ALL blood transfusions require two-person verification of patient identity, blood type, and unit number. Single-person verification is a protocol violation and reportable incident. Supra incident 2024: near-miss due to single verification.',
 'Blood transfusions: two-person verification mandatory.',
 'CONSTRAINT: Two-person verify for transfusion.',
 0.97, 0.95, 0.92, 4, 2, NULL, 72, 18, 9),

('C-03', 'supra', 'CONSTRAINT', 'Antibiotic Stewardship 72-Hour Review',
 'All empiric antibiotics must be reviewed at 72 hours. De-escalate based on culture results. Supra policy: pharmacy auto-alerts at 72 hours if no review documented. Non-compliance flagged to department HOD.',
 'Empiric antibiotics: mandatory 72-hour review with de-escalation.',
 'CONSTRAINT: 72hr antibiotic review mandatory.',
 0.88, 0.88, 0.85, 4, 2, NULL, 68, 20, 9),

('C-04', 'supra', 'CONSTRAINT', 'Fall Risk Assessment on Admission',
 'Every patient assessed for fall risk using Morse Fall Scale on admission and every shift change. Score >= 45: high risk — bed alarm required, yellow wristband, non-slip socks. Staff must document assessment.',
 'Fall risk: Morse Scale on admission + each shift. Score ≥45 = high risk.',
 'CONSTRAINT: Fall risk assessment every shift.',
 0.85, 0.82, 0.78, 4, 2, NULL, 65, 24, 9),

-- ============================================================
-- ZONE 1 ORTHO CONSTRAINTS (Block 4 — always FULL)
-- ============================================================

('C-05', 'supra', 'CONSTRAINT', 'DVT Prophylaxis Protocol',
 'ALL ortho surgical patients receive DVT prophylaxis: Enoxaparin 40mg SC daily starting 12 hours post-op. Duration: 14 days for TKR, 28 days for THR. Contraindication: active bleeding, platelet count < 50,000.',
 'DVT prophylaxis: Enoxaparin 40mg SC daily. TKR 14d, THR 28d.',
 'CONSTRAINT: DVT prophylaxis all ortho surgical.',
 0.93, 0.93, 0.90, 1, 1, 'ortho', 80, 22, 9),

('C-06', 'supra', 'CONSTRAINT', 'Patient Rajan: Absolute NSAID Contraindication',
 'ABSOLUTE CONTRAINDICATION: No ibuprofen, no aspirin, no diclofenac for patient Rajan. Cardiac stent (2022) + dual antiplatelet therapy (Clopidogrel 75mg). Previous 8 NSAID refusals documented. Paracetamol ONLY for pain.',
 'Rajan: NO NSAIDs. Stent + antiplatelet. Paracetamol only.',
 'CONSTRAINT: Rajan — zero NSAIDs.',
 0.99, 0.99, 0.95, 0, 1, 'ortho', 72, 20, 7),

-- ============================================================
-- DECISIONS (Block 3 — compressed by distance)
-- ============================================================

('D-01', 'supra', 'DECISION', 'Paracetamol First-Line Post-TKR',
 'Supra Ortho uses Paracetamol 650mg QDS as first-line post-TKR pain management. Escalation ladder: Step 1 Paracetamol, Step 2 Tramadol 50mg if VAS > 6, Step 3 Morphine 5mg PRN (elderly caution). AVOID NSAIDs at all steps due to surgical site bleeding risk. Decision by Dr. Vikram, January 2025.',
 'Post-TKR pain: Paracetamol 650mg QDS → Tramadol → Morphine. No NSAIDs.',
 'Paracetamol first-line post-TKR.',
 0.88, 0.85, 0.72, 1, 1, 'ortho', 95, 28, 8),

('D-02', 'supra', 'DECISION', 'Zimmer Biomet Implant Preference',
 'Supra Ortho Department uses Zimmer Biomet as preferred TKR implant vendor. Alternative: Smith & Nephew for revision cases only. Decision based on 3-year outcomes review (Dr. Vikram, 2024). Stryker evaluated but rejected (higher cost, similar outcomes).',
 'TKR implant: Zimmer Biomet preferred. S&N for revisions only.',
 'Zimmer Biomet for TKR.',
 0.72, 0.70, 0.55, 2, 1, 'ortho', 78, 24, 6),

('D-03', 'supra', 'DECISION', 'Post-TKR Physiotherapy Start Within 24 Hours',
 'Physiotherapy MUST begin within 24 hours of TKR. Day 1: ankle pumps, static quads. Day 2: CPM machine, assisted standing. Day 3: walker ambulation. Delay beyond 24 hours increases stiffness risk by 3x per Supra audit data.',
 'PT starts within 24h post-TKR. D1 ankle pumps, D2 CPM, D3 walker.',
 'PT within 24h post-TKR mandatory.',
 0.90, 0.88, 0.75, 1, 1, 'ortho', 82, 26, 8),

('D-04', 'supra', 'DECISION', 'Fracture X-Ray Protocol',
 'All suspected fractures: minimum 2 views (AP + lateral). Joint involvement: add oblique view. Growth plate in paeds: compare with contralateral. Digital X-ray preferred over computed radiography.',
 '2-view X-ray minimum for fractures. Add oblique if joint. Digital preferred.',
 'Fracture: 2-view X-ray minimum.',
 0.75, 0.72, 0.48, 2, 1, 'ortho', 70, 22, 7),

('D-05', 'supra', 'DECISION', 'Rajan Pain Management Strategy',
 'Current strategy for Rajan: Paracetamol 650mg QDS + topical Diclofenac gel (minimal systemic absorption). If insufficient: consider intra-articular injection. NO oral NSAIDs under any circumstances. Tramadol trial initiated visit #24.',
 'Rajan pain: Paracetamol QDS + topical Diclofenac. Tramadol trial started.',
 'Rajan: Paracetamol + topical. Tramadol trial.',
 0.82, 0.80, 0.70, 0, 1, 'ortho', 75, 24, 9),

('D-06', 'supra', 'DECISION', 'Ortho Night Shift Handover Protocol',
 'Night shift handover: 15-minute structured handover using SBAR format. Include: pending labs, new admissions past 4 hours, patients for morning surgery, any clinical concerns. Must be documented in ward log.',
 'Night handover: 15min SBAR format. Include pending labs, new admits, surgery list.',
 'SBAR handover at night shift change.',
 0.72, 0.68, 0.42, 2, 1, 'ortho', 68, 24, 7),

('D-07', 'supra', 'DECISION', 'Sepsis Protocol v3 2026',
 'Supra Sepsis Bundle v3 (2026): blood cultures before antibiotics, lactate within 1 HOUR (tightened from v2 which was 3 hours), 30mL/kg crystalloid for hypotension, vasopressors if MAP <65 after fluids.',
 'Sepsis v3: cultures before abx, lactate 1hr, crystalloid 30mL/kg.',
 'Sepsis v3: lactate within 1 hour.',
 0.92, 0.90, 0.65, 3, 1, 'medicine', 72, 24, 8),

('D-08', 'supra', 'DECISION', 'Post-Surgical Pain Escalation Ladder',
 'Pain escalation: Step 1 Paracetamol 650mg QDS → Step 2 Tramadol 50mg TDS → Step 3 Morphine 5mg PRN. Skip Step 2 for elderly >75 (fall risk). VAS assessment every 4 hours.',
 'Pain ladder: Paracetamol → Tramadol → Morphine. Skip Tramadol if >75.',
 'Pain escalation: 3 steps, skip step 2 if elderly.',
 0.80, 0.78, 0.60, 2, 1, 'ortho', 72, 22, 10),

-- ============================================================
-- ANTI_PATTERNS (Block 5 — compressed by distance)
-- ============================================================

('AP-01', 'supra', 'ANTI_PATTERN', 'Never Discharge TKR Under 48 Hours',
 'Do NOT discharge TKR patients before 48 hours post-op. Past incident: patient discharged at 36 hours developed DVT at home, emergency readmission. Minimum 48 hours with physiotherapy assessment and DVT prophylaxis compliance confirmed before discharge.',
 'No TKR discharge < 48h. Past DVT incident after early discharge.',
 'ANTI: No TKR discharge under 48 hours.',
 0.91, 0.88, 0.78, 1, 1, 'ortho', 82, 22, 9),

('AP-02', 'supra', 'ANTI_PATTERN', 'Weight-Bearing Before X-Ray Confirmation',
 'NEVER allow weight-bearing on a fractured limb before X-ray confirmation of alignment. Past incident: tibial fracture patient allowed to stand, causing displacement requiring surgery instead of conservative management.',
 'No weight-bearing before X-ray confirms alignment.',
 'ANTI: No weight-bearing before X-ray.',
 0.89, 0.85, 0.72, 2, 1, 'ortho', 75, 20, 8),

('AP-03', 'supra', 'ANTI_PATTERN', 'Verbal Orders Without Documentation',
 'NEVER accept verbal orders for medication changes without written/electronic confirmation within 1 hour. Exception: cardiac arrest only. Supra incident 2023: wrong dose from mishearing.',
 'No verbal med orders without written confirmation in 1 hour.',
 'ANTI: No verbal orders without documentation.',
 0.90, 0.87, 0.75, 4, 2, NULL, 68, 20, 9),

('AP-04', 'supra', 'ANTI_PATTERN', 'Insulin Sliding Scale Alone',
 'Do NOT use insulin sliding scale as sole glycemic management. Past incident: DKA readmission in 48 hours. Always include basal insulin. Sliding scale supplements, never replaces.',
 'No sliding scale alone — always add basal insulin.',
 'ANTI: Sliding scale alone = bad.',
 0.87, 0.82, 0.55, 3, 1, 'medicine', 65, 20, 8),

-- ============================================================
-- FACTS (Block 5 — most likely to be compressed/omitted)
-- ============================================================

('F-01', 'supra', 'FACT', 'Rajan Medication Profile',
 'Rajan, 68M. Warfarin 5mg daily (AF). Clopidogrel 75mg daily (post-stent 2022). Paracetamol 650mg QDS (knee OA). Atorvastatin 40mg HS. Topical Diclofenac gel PRN. INR target 2.0-3.0, last checked 2.4 (3 days ago).',
 'Rajan: Warfarin 5mg, Clopidogrel 75mg, Paracetamol QDS, Atorvastatin 40mg.',
 'Rajan meds: Warfarin, Clopidogrel, Paracetamol.',
 0.85, 0.82, 0.65, 0, 1, 'ortho', 88, 28, 9),

('F-02', 'supra', 'FACT', 'Rajan Behavioral: NSAID Requests',
 'Patient Rajan repeatedly requests Ibuprofen for knee pain despite 8 documented refusals. Family (son) also requests. Counseled each visit. Behavioral note for future visits: expect NSAID request, be firm, explain why.',
 'Rajan still asks for Ibuprofen (8 refusals). Family also asks.',
 'Rajan: expects NSAID request — refuse.',
 0.72, 0.68, 0.45, 0, 1, 'ortho', 72, 22, 8),

('F-03', 'supra', 'FACT', 'Ortho Ward Bed Capacity',
 'Ortho Ward: 45 beds total. 12 post-surgical, 8 traction, 25 general ortho. Usual occupancy 85-90%. Winter peak (fractures): 100%+, overflow to Medicine Ward arranged with Dr. Meera.',
 'Ortho: 45 beds. 85-90% typical. Overflow to Medicine in winter.',
 'Ortho: 45 beds.',
 0.50, 0.45, 0.20, 3, 1, 'ortho', 65, 22, 5),

('F-04', 'supra', 'FACT', 'Ortho Nurse-Patient Ratio',
 'Ortho Ward nurse-patient ratio: 1:6 (day), 1:8 (night). Post-surgical first 24 hours: 1:4. ICU step-down patients: 1:2 until stable.',
 'Nurse ratio: 1:6 day, 1:8 night, 1:4 post-op.',
 'Nurse ratio: 1:6 day.',
 0.55, 0.50, 0.22, 3, 1, 'ortho', 52, 18, 6),

('F-05', 'supra', 'FACT', 'Supra Formulary Preferences',
 'Supra formulary preferred brands: Paracetamol (Calpol/Dolo), Omeprazole (Omez), Amoxicillin (Mox), Metformin (Glycomet). Use formulary brand unless clinical reason documented.',
 'Formulary: Calpol/Dolo, Omez, Mox, Glycomet.',
 'Formulary brands for common drugs.',
 0.65, 0.60, 0.32, 3, 2, NULL, 58, 18, 7),

('F-06', 'supra', 'FACT', 'Supra Emergency Codes',
 'Code Blue: cardiac arrest. Code Red: fire. Code Pink: infant abduction. Code Grey: combative patient. Code Orange: mass casualty. All staff must know codes for their floor.',
 'Codes: Blue=arrest, Red=fire, Pink=abduction, Grey=combative.',
 'Emergency codes: Blue, Red, Pink, Grey, Orange.',
 0.70, 0.65, 0.30, 4, 2, NULL, 55, 22, 10),

('F-07', 'supra', 'FACT', 'Patient Padma: Fasting Pattern',
 'Padma 62F, Type 2 DM. Observes Ekadashi fasting twice monthly. Adjusted protocol: skip Glimepiride on fast days, continue Metformin with evening meal. 3 hypoglycemia episodes in 2025 before protocol adjustment.',
 'Padma: skip Glimepiride on Ekadashi, continue Metformin.',
 'Padma: fasting DM protocol adjusted.',
 0.78, 0.72, 0.50, 3, 1, 'medicine', 68, 22, 8),

('F-08', 'supra', 'FACT', 'Ortho Department Implant Costs',
 'Average TKR implant cost at Supra: ₹1.8L (Zimmer). Revision: ₹2.5L (S&N). Budget allocation: 45% of dept budget to implants. Volume discount negotiation pending July 2026.',
 'TKR implant: ₹1.8L Zimmer. Revision ₹2.5L. 45% of budget.',
 'TKR implant costs and budget.',
 0.45, 0.40, 0.15, 3, 1, 'ortho', 62, 22, 7),

-- ============================================================
-- STALE NODE (Block 7 — for stale flags demo)
-- ============================================================

('S-01', 'supra', 'DECISION', 'Sepsis Protocol v2 2024 (SUPERSEDED)',
 'OLD: Supra Sepsis Bundle v2 (2024): blood cultures before antibiotics, lactate within 3 HOURS. SUPERSEDED by v3 (2026) which tightened to 1 hour. THIS NODE IS FLAGGED FOR REVIEW.',
 'STALE: Sepsis v2 superseded by v3. Lactate window was 3h, now 1h.',
 'STALE: Old Sepsis v2 — replaced by v3.',
 0.50, 0.45, 0.20, 3, 1, 'medicine', 72, 24, 9);

-- Set stale node status
UPDATE candidate_nodes SET status = 'REVIEW_REQUIRED' WHERE id = 'S-01';
```

---

## SYSTEM PROMPT TEMPLATE (~800 tokens)

```python
SYSTEM_PROMPT = """You are BRAHMO, an organizationally-aware AI assistant.
You have been provided with structured context from {org_name}'s knowledge
graph. This context has been filtered for {user_name}'s role ({user_role})
and permission level, and assembled specifically for this session.

RULES:
1. Apply the organizational context below to every response.
2. CONSTRAINT nodes are non-negotiable safety rules — never suggest
   actions that violate them.
3. If you don't have sufficient context to answer confidently, say so
   rather than guessing.
4. Reference specific organizational decisions when relevant
   ("per Supra's post-TKR protocol...").
5. If the user shares new decisions or constraints worth remembering,
   note them at the end of your response with the prefix CAPTURE:
   so they can be reviewed for knowledge graph storage.

{composed_context_string}
"""
```

---

## TOKEN COUNTING UTILITY

```python
# backend/composition/token_counter.py
import tiktoken

_encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens using cl100k_base (Claude-compatible)."""
    return len(_encoder.encode(text))

def count_three_sources(
    system_prompt: str,
    context_string: str,
    user_message_estimate: int = 200
) -> dict:
    """Count all THREE token sources BEFORE API call."""
    system_tokens = count_tokens(system_prompt)
    context_tokens = count_tokens(context_string)
    
    return {
        "system_prompt_tokens": system_tokens,
        "context_tokens": context_tokens,
        "user_message_tokens": user_message_estimate,
        "total": system_tokens + context_tokens + user_message_estimate,
        "budget": 4000,
        "remaining": 4000 - (system_tokens + context_tokens + user_message_estimate),
        "over_budget": (system_tokens + context_tokens + user_message_estimate) > 4000
    }
```

---

## EXPECTED COMPOSITION RESULTS

### Dr. Vikram + Mr. Rajan (budget: 4,000)

| Stage | Tokens | Notes |
|-------|:------:|-------|
| System prompt | 800 | Fixed |
| User reserve | 200 | Estimated |
| **Available for context** | **3,000** | |
| 28 nodes at FULL | 4,200 | Over by 1,200 |
| Pass 1: compress distance-3+ FACTs | -520 | F-03, F-04, F-08 → OMIT; F-05, F-06 → CONSTRAINT_ONLY |
| Pass 2: compress distance-2 DECISIONs | -380 | D-04, D-06 → COMPRESSED; AP-02 → COMPRESSED |
| Pass 3: compress distance-3 items | -340 | D-07, AP-04, F-07 → CONSTRAINT_ONLY |
| **Final context** | **~2,960** | Under budget ✅ |
| **Total (3-source)** | **~3,960** | Under 4,000 ✅ |

**Protected (FULL throughout):** C-01, C-02, C-03, C-04, C-05, C-06 — all CONSTRAINT nodes

### Final Block Allocation:

| Block | Content | Tokens |
|-------|---------|:------:|
| 1: Role Frame | "You are assisting Dr. Vikram, HOD Orthopaedics..." | ~80 |
| 2: Global Constraints | C-01, C-02, C-03, C-04 (all FULL) | ~290 |
| 3: Recent Decisions | D-01, D-03, D-05 (FULL); D-02, D-08 (COMPRESSED) | ~380 |
| 4: Active Constraints | C-05, C-06 (all FULL) | ~152 |
| 5: Session Context | F-01, F-02 (FULL); AP-01 (FULL); rest COMPRESSED/C_ONLY | ~850 |
| 6: Open Questions | (empty) | 0 |
| 7: Stale Flags | S-01 (CONSTRAINT_ONLY) | ~50 |
| 8: Boundaries | CAPTURE instruction | ~100 |
| **Total** | | **~2,960** |

---

## SUBMISSION CHECKLIST

```
□ 28 candidate nodes loaded with pre-generated content at 3 compression levels
□ Token counter uses tiktoken (not character count approximation)
□ ALL THREE sources counted: system prompt + context + user reserve
□ Count happens BEFORE any API call
□ 8 blocks assembled in correct order (1-8, never reordered)
□ CONSTRAINTs in Block 2 (global) and Block 4 (department)
□ Distance-weighted compression assigns correct default levels
□ CONSTRAINT nodes ALWAYS FULL regardless of distance
□ Iterative compression runs when over budget
□ Lowest injection_weight non-CONSTRAINT compressed first
□ Compression stops when under budget
□ Budget visualization shows 3-source breakdown
□ Per-node detail shows dual weights (retrieval + injection)
□ Compression log shows pass-by-pass reduction
□ Budget slider changes composition dynamically
□ Block 7 (Stale) only appears when REVIEW_REQUIRED nodes exist
□ Block 8 has CAPTURE: instruction text
□ Final context string viewable
□ docs/architecture.md explains compression ordering + CONSTRAINT protection
□ Clean git, README present
```

---

## FREE TIER SUFFICIENCY

| Resource | Free Tier | Sufficient? |
|---|---|---|
| **Supabase** | 500 MB, 50K rows | YES — 28 nodes trivial |
| **LLM API** | $5 credit | YES — only for chat demo after composition |
| **tiktoken** | Free (pip install) | YES |

**Total cost: $0**

---

*Setup Guide v1.0 — Token Budget + Iterative Compression*
