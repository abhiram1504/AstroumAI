# DEVELOPER ASSESSMENT 4: Make Every Token Count
## Token Budget + 8-Block Assembly + Iterative Compression
### BRAHMO — Full-Stack Developer Assessment

**Time:** 5-8 hours | **Demo:** 20-25 minutes | **Deadline:** 72 hours
**Stack:** Supabase + Python (FastAPI) OR Node.js + React + any LLM API + Tailwind CSS
**Tools:** Use ANY AI tool — no paid subscriptions required (see Setup Guide)
**Deliverables:** Working demo + source code + architecture notes

---

## THE STORY THAT STARTED THIS (Why This Matters)

Dr. Vikram, the Orthopaedics HOD at Supra Hospital, opens an AI session to discuss Mr. Rajan's pain management. The Rules Engine has done its job — from 842 knowledge nodes, it produced 28 candidates: drug safety constraints, surgical protocols, patient-specific facts, departmental decisions, and global hospital policies.

If you dump all 28 nodes raw into the AI's system prompt, you get 4,200 tokens of context. The AI's token budget is 4,000. Add the system prompt (800 tokens) and an estimated user message (200 tokens), and you're at 5,200 total — blowing past the ceiling before the AI even responds.

But the problem isn't just size — it's STRUCTURE. A raw dump puts a drug safety constraint ("NEVER give Rajan NSAIDs") at the same priority as a ward capacity fact ("Ortho has 45 beds"). The AI treats them equally. It might mention the bed count before mentioning the life-threatening drug interaction.

The Composition Agent solves both problems at once: it scores each node with dual importance weights, sorts them into 8 structured blocks (global constraints FIRST, recent decisions NEXT, session-specific details LAST), applies distance-weighted compression (nearby nodes get full content, distant ones get summaries), and iteratively compresses until everything fits within 3,000 tokens — all while protecting CONSTRAINT nodes from EVER being compressed.

**Your job:** Build the system that transforms 28 raw candidate nodes into a structured, token-efficient, priority-ordered context string that fits within a hard 4,000-token ceiling — with every token earning its place.

---

## WHAT YOU'RE BUILDING (2-minute read)

A Composition Agent that receives candidate nodes from the Rules Engine, applies dual importance scoring, assembles them into 8 structured blocks, enforces a hard token ceiling with iterative compression, and outputs a context string ready for system-level injection into the AI.

**The data flow:**
```
28 candidate nodes from Rules Engine arrive:
  → Dual Importance Scoring (~20ms):
    ├── Retrieval weight (from Rules Engine): 0.5-1.0
    │   High retrieval = important for RECALL (don't miss it)
    └── Injection weight (new, for Composition): 0.1-1.0
        High injection = deserves more TOKENS (full content)
        CONSTRAINT: retrieval 0.95 + injection 0.90 = full content always
        FACT: retrieval 0.60 + injection 0.30 = compressed first

  → 8-Block Assembly (~30ms):
    Block 1: Role Frame ("You are assisting Dr. Vikram, HOD Ortho...")
    Block 2: Zone 2 Global Constraints (drug safety, hospital policies)
    Block 3: Recent Decisions (last 30 days, highest injection weight)
    Block 4: Active Constraints (department-specific, ALWAYS FULL)
    Block 5: Session-Specific Context (patient facts, procedures)
    Block 6: Open Questions (v0.2 — empty placeholder)
    Block 7: Stale Flags (REVIEW_REQUIRED nodes as warnings)
    Block 8: Session Boundaries (CAPTURE: instruction for post-session)

  → Distance-Weighted Compression (~40ms):
    Distance 0-1 from entry point: FULL content (~150 tokens/node)
    Distance 2: COMPRESSED (~50 tokens/node, key facts only)
    Distance 3+: CONSTRAINT_ONLY (~20 tokens/node, just the rule)
    EXCEPTION: CONSTRAINT nodes = ALWAYS FULL regardless of distance

  → Token Budget Enforcement (~50ms):
    ├── Count ALL THREE sources:
    │   System prompt:    800 tokens
    │   Context string:  4,200 tokens (at FULL) ← OVER BUDGET
    │   User message:     200 tokens (estimated)
    │   Total:           5,200 tokens ← exceeds 4,000 ceiling
    │
    ├── Iterative Compression Loop:
    │   Pass 1: compress distance-3+ FACTs to CONSTRAINT_ONLY → saves ~800
    │   Pass 2: compress distance-2 DECISIONs to COMPRESSED → saves ~500
    │   Pass 3: check → 3,900 tokens total ← UNDER BUDGET ✅
    │
    └── NEVER compress: CONSTRAINT nodes (even if over budget, compress others first)

  → Output: Structured context string (3,000 tokens) + composition metadata
```

**What we provide:** 28 pre-scored candidate nodes with types, importance values, distances, and zone assignments. 8-block template. Token counting utility. — all in Setup Guide.

**What you figure out (25-30%):** Compression algorithm ordering, iterative loop termination conditions, how to handle edge cases (all CONSTRAINTs exceed budget alone), block token allocation strategy.

---

## HOW TO THINK ABOUT THIS (Read Before You Code)

### Mental Model

Think of the Composition Agent as a newspaper editor with a fixed page count:

**The dual importance is like editorial judgment:** A war correspondent's report (CONSTRAINT, high retrieval + high injection) gets the front page, full column. A weather update (FACT, moderate retrieval + low injection) gets a one-line mention. Both were "retrieved" (found newsworthy), but they get very different SPACE.

**The 8-block structure is like newspaper sections:** Breaking news (Block 2: global constraints) always runs first. Recent local events (Block 3: decisions) follow. The classified section (Block 5: session context) fills remaining space. The editor never puts classifieds before breaking news.

**Iterative compression is like cutting for space:** When the page is full, you don't cut the lead story — you trim the least important pieces first. Facts get summarized. Decisions get their headline only. Constraints are never cut.

**The token budget is the page count:** Hard limit. If you print 41 pages in a 40-page paper, the press breaks. You count BEFORE printing, not after.

### Decision Priority

| Priority | Component | Why | Time Allocation |
|---|---|---|---|
| 1 | Token budget enforcement (3-source counting + iterative compression) | The CORE — prevents overspend, protects constraints | 30% |
| 2 | 8-block assembly with correct ordering | Structure determines AI quality | 20% |
| 3 | Distance-weighted compression with CONSTRAINT protection | Token efficiency without safety loss | 20% |
| 4 | Dual importance scoring + visualization | Makes composition decisions VISIBLE | 15% |
| 5 | Innovation | Your 25-30% | 15% |

**The single most important thing:** The token count must be computed BEFORE the AI API call is made, using ALL THREE sources (system prompt + context string + estimated user message). If you count after the call, the overspend already happened. If you count only the context string and miss the system prompt, you're undercounting by 30-40%.

### What NOT to Overthink

- Don't build the Rules Engine — the 28 candidates are pre-seeded with distances and zones
- Don't build streaming chat — showing the composed context string and its token count is sufficient
- Don't use an LLM for composition decisions — composition ordering and compression are DETERMINISTIC (the LLM is used for the chat AFTER composition, not for composition itself)
- Don't build real Clerk auth — user selection dropdown
- Don't optimize for 500 nodes — 28 candidates demonstrating the pattern is sufficient

---

## WHAT YOUR FINISHED PRODUCT LOOKS LIKE

**Main View — Composition Pipeline:**
```
┌──────────────────────────────────────────────────────────────────┐
│  BRAHMO Composition Agent — Token Budget + 8-Block Assembly       │
│                                                                  │
│  User: [▼ Dr. Vikram — HOD, Ortho]  Patient: [▼ Mr. Rajan]     │
│  Token Budget: 4,000 | System Prompt: 800 | User Reserve: 200   │
│  Available for context: 3,000 tokens                             │
│  [Compose Context]                                               │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TOKEN BUDGET VISUALIZATION:                                     │
│  ┌────────────────────────────────────────────────────────┐      │
│  │ ██████ System Prompt (800)                              │      │
│  │ ████████████████████████████ Context (2,840)            │      │
│  │ ███ User Reserve (200)                                  │      │
│  │ ░░ Remaining (160)                                      │      │
│  └──────────────────────────────── 4,000 ceiling ─────────┘      │
│                                                                  │
│  COMPOSITION SUMMARY:                                            │
│  28 candidates → 22 included, 6 omitted                          │
│  Compression: 8 FULL | 10 COMPRESSED | 4 CONSTRAINT_ONLY        │
│  Iterations: 3 passes to fit within budget                       │
│  CONSTRAINT nodes: 6/6 at FULL (never compressed) ✅             │
│                                                                  │
├───────────────────────┬──────────────────────────────────────────┤
│ 8-BLOCK STRUCTURE     │ COMPOSITION DETAIL                       │
│                       │                                          │
│ Block 1: Role Frame   │ ┌─ Node N-G01 ─────────────────────┐    │
│ ██ 80 tokens          │ │ Type: 🔴 CONSTRAINT               │    │
│                       │ │ Title: Warfarin-NSAID Interaction  │    │
│ Block 2: Global Const │ │ Retrieval: 0.98  Injection: 0.95  │    │
│ ████ 420 tokens       │ │ Distance: 4  Compression: FULL    │    │
│                       │ │ Block: 2 (Global Constraints)      │    │
│ Block 3: Decisions    │ │ Tokens: 85                         │    │
│ ██████ 580 tokens     │ │ ✅ CONSTRAINT — never compressed   │    │
│                       │ └────────────────────────────────────┘    │
│ Block 4: Constraints  │                                          │
│ ████ 400 tokens       │ ┌─ Node N-O05 ─────────────────────┐    │
│                       │ │ Type: 🔵 FACT                      │    │
│ Block 5: Session Ctx  │ │ Title: Ortho Ward Bed Capacity     │    │
│ ████████ 760 tokens   │ │ Retrieval: 0.50  Injection: 0.25  │    │
│                       │ │ Distance: 3  Compression: OMIT     │    │
│ Block 6: Open Q       │ │ Block: — (OMITTED)                 │    │
│ (empty — v0.2)        │ │ Reason: Low injection weight,      │    │
│                       │ │         budget pressure             │    │
│ Block 7: Stale Flags  │ └────────────────────────────────────┘    │
│ █ 50 tokens           │                                          │
│                       │ [Show all 28 nodes with include/exclude] │
│ Block 8: Boundaries   │ [Show composition rationale per node]    │
│ ██ 100 tokens         │ [View assembled context string]          │
└───────────────────────┴──────────────────────────────────────────┘
```

**Iterative Compression Visualization:**
```
┌──────────────────────────────────────────────────────────────────┐
│  ITERATIVE COMPRESSION LOG                                        │
│                                                                  │
│  Initial: 28 nodes at FULL = 4,200 tokens                       │
│  Budget:  3,000 tokens for context                               │
│  Over by: 1,200 tokens ❌                                        │
│                                                                  │
│  Pass 1: Compress distance-3+ FACTs                              │
│  ├── N-D01 (What is TKR): FULL → OMIT          saved 120 tokens │
│  ├── N-O05 (Bed capacity): FULL → OMIT          saved 95 tokens  │
│  ├── N-O08 (Nurse ratio): FULL → CONSTRAINT_ONLY saved 110 tokens│
│  └── ... 3 more                                                  │
│  After pass 1: 3,400 tokens — still over by 400 ❌              │
│                                                                  │
│  Pass 2: Compress distance-2 DECISIONs                           │
│  ├── N-O07 (X-ray protocol): FULL → COMPRESSED   saved 85 tokens │
│  ├── N-O15 (Handover): FULL → COMPRESSED          saved 90 tokens│
│  └── ... 2 more                                                  │
│  After pass 2: 2,840 tokens — under budget ✅                   │
│                                                                  │
│  PROTECTED (never compressed):                                   │
│  ├── N-G01 CONSTRAINT: Warfarin-NSAID           FULL (85 tokens) │
│  ├── N-O14 CONSTRAINT: Rajan NSAID ban          FULL (72 tokens) │
│  ├── N-O06 CONSTRAINT: DVT Prophylaxis          FULL (80 tokens) │
│  └── ... 3 more CONSTRAINT nodes                                 │
│                                                                  │
│  3 iterations | 22 nodes included | 6 omitted | Budget: ✅       │
└──────────────────────────────────────────────────────────────────┘
```

---

## DEMO SCENARIOS (Run all 4)

### Scenario 1: "The Full Pipeline" (28 → Structured Context)
**Action:** Select Dr. Vikram + Mr. Rajan. Click "Compose Context."
**What to show:** 28 candidates arrive. Dual importance scored. Sorted into 8 blocks. Token budget computed (3-source). Iterative compression runs 2-3 passes. Final context string: structured, under 3,000 tokens. Show the budget bar filling — system prompt (800) + context (2,840) + user reserve (200) = 3,840, under 4,000 ceiling.

**What we're evaluating:** Are ALL THREE sources counted? Is the budget checked BEFORE any API call? Does the iteration terminate correctly? Are CONSTRAINT nodes still at FULL after compression?

### Scenario 2: "CONSTRAINT Protection" (The Sacred Rule)
**Action:** Point to the 6 CONSTRAINT nodes in the composition output.
**What to show:** ALL 6 CONSTRAINT nodes are at FULL compression — even the one at distance 4 (farthest from entry point). Meanwhile, a FACT at distance 1 (near the entry point) was compressed to CONSTRAINT_ONLY because it had low injection weight. Show: distance determines DEFAULT compression, but type OVERRIDES distance for CONSTRAINTs. A CONSTRAINT is never compressed. If compressing all non-CONSTRAINTs still doesn't fit budget, the system OMITS low-importance nodes rather than compressing CONSTRAINTs.

**Critical test:** Add a scenario where CONSTRAINTs alone exceed 3,000 tokens. What happens? (Answer: all non-CONSTRAINTs are OMITTED, CONSTRAINTs are FULL, and if still over — flag for human override, do NOT truncate CONSTRAINTs.)

### Scenario 3: "Dual Importance — Retrieval vs Injection"
**Action:** Show two nodes with different weight profiles.
**What to show:** Node A (CONSTRAINT, "Warfarin-NSAID never combine"): retrieval weight 0.95, injection weight 0.90. Gets 85 tokens, FULL content, Block 2. Node B (FACT, "Ortho Ward has 45 beds"): retrieval weight 0.50, injection weight 0.25. Gets OMITTED — retrieved for completeness but not worth injecting. Show: retrieval weight determined WHETHER the node was in the candidate set (Rules Engine decision). Injection weight determines HOW MUCH SPACE it gets (Composition Agent decision). Two different weights for two different purposes.

### Scenario 4: "Change Budget — Watch Compression Adapt"
**Action:** Change the token budget from 4,000 to 2,000 (slider or input).
**What to show:** The iterative compression runs more aggressively. More nodes move from FULL to COMPRESSED to CONSTRAINT_ONLY to OMIT. But CONSTRAINTs stay at FULL. The composition quality degrades gracefully — not by truncating critical safety info, but by summarizing and omitting less important facts. Show the compression visualization changing in real time as the budget slider moves.

---

## SURPRISE TEST (CRITICAL — READ THIS)

After your 4 demos, we change the input:

**Example:** "Remove 20 candidates — only 8 remain, all CONSTRAINTs. Total at FULL = 1,200 tokens. Budget = 3,000. What happens?"

**What we're testing:**
- No compression needed — all 8 fit at FULL
- The system doesn't compress unnecessarily
- The remaining 1,800 tokens of budget are UNUSED (not filled with padding)
- Block 2 and Block 4 are populated; other blocks may be empty

**Alternative surprise:** "Add 40 candidates instead of 28. Total at FULL = 6,500 tokens."
- More aggressive compression needed
- More nodes OMITTED
- CONSTRAINTs still protected
- The system handles gracefully without crashing

**The Architecture Question:**
"A software company with 50 engineers has 10 sessions per day each. Each session costs ~$0.05 in tokens. Without composition, each session costs ~$0.12 (raw injection). What's the annual savings?"

**Right answer:** "50 × 10 × ($0.12 - $0.05) × 250 working days = $8,750/year. Composition reduces token usage by ~58%. At scale (500 engineers), that's $87,500/year in API cost savings — just from smart compression."

---

## WHAT 10/10 LOOKS LIKE

*"The iterative compression visualization was brilliant — I could see each pass removing tokens from the lowest-priority nodes while CONSTRAINTs stayed untouched. The 3-source counting caught what I'd normally miss: the system prompt alone is 800 tokens, and without counting it, you'd blow the budget on every session. When I moved the budget slider from 4,000 to 2,000, the composition degraded gracefully — facts got summarized, decisions got headlines, but drug safety constraints stayed at full content. That's the difference between a system that truncates and a system that composes. The dual importance was the insight — retrieval weight asks 'should this be HERE?' and injection weight asks 'how much SPACE should it get?' Two different questions, two different weights."*

---

## OPEN-ENDED THINKING GUIDE (Your 25-30%)

### Problem 1: "What if CONSTRAINTs alone exceed the budget?"
6 CONSTRAINT nodes at FULL = 900 tokens. Budget = 3,000. Fine. But what if there are 25 CONSTRAINTs totaling 3,500 tokens? Budget exceeded with only CONSTRAINTs — and they can't be compressed. Do you raise the budget ceiling? Omit some CONSTRAINTs? Flag for human override? What's the safest failure mode?

### Problem 2: "Accurate token counting without the tokenizer"
Production uses Anthropic's tokenizer (tiktoken-compatible). But for the demo, you may not have it. Character count approximation (÷4) is 30-40% inaccurate. Word count (×1.3) is better but still off. How do you handle counting? If you OVER-count, you exclude good nodes unnecessarily. If you UNDER-count, you blow the budget. Show your approach and its accuracy.

### Problem 3: "Block token allocation"
The 8 blocks don't all get equal space. Block 2 (global constraints) gets however much it needs — CONSTRAINTs are never compressed. Block 5 (session context) gets the remaining space. But what if Block 3 (recent decisions) has 15 nodes and Block 5 has 2? How do you allocate tokens across blocks? Fixed allocation per block, or dynamic based on content?

### Problem 4: "Compression quality — summarizing vs truncating"
COMPRESSED level means "key facts only, ~50 tokens." But how do you actually compress? Option A: use an LLM to summarize (accurate but slow + costs tokens). Option B: use the first N sentences (fast but may miss the key point). Option C: pre-compute compressed versions at node creation time (fast at composition but storage overhead). What's your approach?

### Problem 5: "The human override"
Dr. Vikram notices that node N-O07 (fracture X-ray protocol) was OMITTED due to low injection weight. But he's about to discuss Rajan's X-ray results. He wants to force-include it. How does the override work? Does it push something else out (to stay within budget)? Is the override saved for future sessions with Rajan?

---

## EVALUATION CRITERIA

| Criteria | Weight | 10/10 looks like |
|----------|:------:|-----------------|
| **Token budget enforcement** | 30% | ALL THREE sources counted (system + context + user). Counted BEFORE any API call. Iterative compression runs until under budget. Budget violation is impossible — system rejects if can't fit. |
| **8-block assembly** | 20% | Blocks in correct order (1-8). CONSTRAINTs in Block 2/4, DECISIONs in Block 3, session context in Block 5. Block 8 has CAPTURE instruction. No blocks reordered. |
| **Distance-weighted compression + CONSTRAINT protection** | 25% | Distance determines default level. CONSTRAINT nodes ALWAYS FULL regardless of distance. Lowest-importance nodes compressed first. Iterative loop visible. |
| **Dual importance visualization** | 15% | Retrieval vs injection weights visible per node. The evaluator can see WHY a node was included/excluded/compressed. Composition rationale is transparent. |
| **Innovation** | 10% | Solves a real problem from thinking guide. Shows understanding of budget allocation, compression quality, or override design. |

---

## COMMON PITFALLS

- ❌ Not counting system prompt tokens → budget exceeded by 800 tokens silently
- ❌ Not counting estimated user message → 200-token user query pushes over ceiling
- ❌ Compressing CONSTRAINT nodes first (they're large) → safety-critical info lost
- ❌ Counting after the API call → overspend already happened
- ❌ Using character count instead of token count → inaccurate by 30-40%
- ❌ No iterative fallback → single-pass either fits or fails
- ❌ Making the API call even when over budget → wasted spend
- ❌ Reordering the 8 blocks → injection order is locked
- ❌ Including Block 7 (Stale Flags) when no REVIEW_REQUIRED nodes exist → empty block waste
- ❌ Using an LLM for compression decisions → composition ordering is DETERMINISTIC
- ❌ Hardcoded block sizes → must adapt to actual content

---

## PRE-DEMO CHECKLIST

```
□ 28 candidate nodes loaded with type, importance, distance, zone
□ Dual importance weights computed (retrieval + injection per node)
□ 8-block template configured with correct ordering
□ Token counter works (tiktoken or approximation with known accuracy)
□ System prompt tokens counted (~800)
□ User message reserve counted (~200)
□ Context tokens counted for all 28 nodes at FULL
□ Initial count exceeds budget (4,200 > 3,000) — proves compression needed
□ Iterative compression runs 2-3 passes to fit
□ All 6 CONSTRAINT nodes remain at FULL after compression
□ Lowest-importance FACTs compressed first
□ Budget visualization shows 3-source breakdown
□ Composition metadata shows include/exclude reason per node
□ Budget slider changes compression behavior in real time
□ 8-block output viewable as structured text
□ Block 8 contains CAPTURE: instruction text
□ docs/architecture.md explains compression ordering + CONSTRAINT protection
□ Clean git, README present
```

---

## FAQ

**Q: Do I need to build the Rules Engine to produce the 28 candidates?**
A: No. The 28 candidates are pre-seeded in the Setup Guide with all metadata (type, importance, distance, zone). Your Composition Agent receives them as input.

**Q: Do I need an LLM for the composition itself?**
A: No. Composition ordering, compression, and block assignment are DETERMINISTIC. An LLM is needed only for the CHAT after composition (to show the AI using the composed context). For the demo, showing the composed context string and its metrics is the primary deliverable.

**Q: How do I count tokens accurately?**
A: Best: `tiktoken` library (Python) with `cl100k_base` encoding (matches Claude). Acceptable: word count × 1.3. Not acceptable: character count ÷ 4 (too inaccurate). The Setup Guide includes a token counting utility.

**Q: What are the three compression levels?**
A: FULL = complete node content (~150 tokens). COMPRESSED = key facts summary (~50 tokens). CONSTRAINT_ONLY = just the rule/headline (~20 tokens). OMIT = excluded entirely (0 tokens). Each node has `content` (FULL), `content_compressed` (COMPRESSED), and `content_constraint_only` (CONSTRAINT_ONLY) pre-generated in the seed data.

**Q: What if I can't fit all CONSTRAINTs within the budget?**
A: This is Problem 1 from the thinking guide. The recommended approach: flag for human override with a clear message "Budget exceeded by CONSTRAINTs alone — X tokens over. Increase budget or review CONSTRAINT set." Do NOT truncate CONSTRAINTs.

---

## DAY-OF-DEMO

- **Format:** Video call. Screen share. App running before call starts.
- **Duration:** 20-25 minutes. Punctual.
- **Have ready:** 28 candidates loaded. Composition pre-run for Vikram + Rajan. Budget visualization rendering.
- **The money moment:** The iterative compression visualization showing pass 1, pass 2, pass 3 — each removing tokens from the least important nodes while CONSTRAINTs stay full. When the evaluator sees "drug safety at 85 tokens FULL, bed capacity OMITTED" and understands WHY, you've succeeded.
- **Surprise test:** We change the input (fewer/more candidates, different budget). Your system must handle it dynamically.
- **Questions we'll ask:** "What are the three sources you count?" "What if CONSTRAINTs alone exceed the budget?" "Why is retrieval weight different from injection weight?" "Show me the cost savings calculation."

---

## DEMO STRUCTURE (20-25 minutes)

1. **[2 min]** Architecture: Candidates → Dual Importance → 8-Block → Compression → Token Budget → Context String. Emphasize: 3-source counting BEFORE API call.
2. **[5 min]** Scenario 1: Full pipeline. 28 nodes in, structured context out. Budget visualization. Iterative compression log.
3. **[4 min]** Scenario 2: CONSTRAINT protection. Show 6 CONSTRAINTs at FULL. Show a FACT compressed despite being closer. Explain the override.
4. **[4 min]** Scenario 3: Dual importance. Compare high-retrieval-high-injection (CONSTRAINT) vs high-retrieval-low-injection (FACT). Show why both were retrieved but treated differently.
5. **[3 min]** Scenario 4: Budget slider. Move from 4,000 to 2,000. Watch compression adapt. CONSTRAINTs untouched.
6. **[2 min]** Your innovation — which problem did you solve?
7. **[5 min]** Surprise input change + cost savings question + our questions

---

*Version: 1.0 | BRAHMO Core — Knowledge Infrastructure*
*Seed data, 28 candidate nodes, 8-block template, and setup instructions are in the separate Setup Guide document.*
