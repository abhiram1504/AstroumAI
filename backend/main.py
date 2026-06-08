import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv

from backend.models.candidate import CandidateNode
from backend.composition.importance_scorer import score_nodes
from backend.composition.compressor import assign_initial_compression
from backend.composition.block_assembler import assemble_blocks, SYSTEM_PROMPT_TEMPLATE
from backend.composition.budget_fitter import run_budget_fitter, build_context_string_from_blocks
from backend.composition.token_counter import count_three_sources, count_tokens
from backend.composition.context_builder import build_metadata

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client with environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase = create_client(supabase_url, supabase_key)

class ComposeRequest(BaseModel):
    user_id: str
    patient_id: str
    token_budget: int = 4000

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users")
def get_users():
    res = supabase.table("users").select("*").execute()
    return res.data

@app.get("/patients")
def get_patients():
    res = supabase.table("patients").select("*").execute()
    return res.data

@app.post("/compose")
def compose(req: ComposeRequest):
    # 1. Fetch user and patient
    user_res = supabase.table("users").select("*").eq("id", req.user_id).execute()
    patient_res = supabase.table("patients").select("*").eq("id", req.patient_id).execute()

    if not user_res.data:
        raise HTTPException(status_code=404, detail="User not found")
    if not patient_res.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    user = user_res.data[0]
    patient = patient_res.data[0]

    # 2. Fetch all 28 candidate nodes
    nodes_res = supabase.table("candidate_nodes").select("*").execute()
    raw_nodes = nodes_res.data

    # 3. Convert to CandidateNode objects
    nodes = []
    for n in raw_nodes:
        nodes.append(CandidateNode(
            id=n["id"],
            org_id=n["org_id"],
            type=n["type"],
            title=n["title"],
            content_full=n["content_full"],
            content_compressed=n["content_compressed"],
            content_constraint_only=n["content_constraint_only"],
            importance=float(n["importance"]),
            retrieval_weight=float(n["retrieval_weight"]),
            injection_weight=float(n["injection_weight"]),
            distance_from_entry=int(n["distance_from_entry"]),
            zone=int(n["zone"]),
            department=n.get("department"),
            status=n.get("status", "ACTIVE"),
            tokens_full=int(n["tokens_full"]),
            tokens_compressed=int(n["tokens_compressed"]),
            tokens_constraint_only=int(n["tokens_constraint_only"])
        ))

    # 4. Score nodes (adds composite_score)
    nodes = score_nodes(nodes)

    # 5. Assign initial compression levels based on distance
    for node in nodes:
        assign_initial_compression(node)

    # 6. Assemble into 8 blocks
    blocks = assemble_blocks(nodes, user, patient)

    # 7. Build system prompt (to count its tokens)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        org_name="Supra Multi-Specialty Hospital",
        user_name=user["name"],
        user_role=user["role"],
        composed_context_string="[CONTEXT]"
    )
    system_tokens = count_tokens(system_prompt)

    # 8. Run iterative budget fitter
    SYSTEM_PROMPT_RESERVE = int(os.getenv("SYSTEM_PROMPT_RESERVE", 800))
    USER_RESERVE = int(os.getenv("USER_MESSAGE_RESERVE", 200))

    final_context, compression_log, error = run_budget_fitter(
        blocks=blocks,
        all_nodes=nodes,
        user=user,
        patient=patient,
        token_budget=req.token_budget,
        system_prompt_tokens=SYSTEM_PROMPT_RESERVE,
        user_reserve=USER_RESERVE
    )

    # 9. Count final tokens (3-source)
    token_breakdown = count_three_sources(system_prompt, final_context, USER_RESERVE)

    # 10. Build metadata for frontend
    metadata = build_metadata(nodes, blocks)

    # 11. Count stats
    included = [n for n in nodes if not n.omitted]
    omitted = [n for n in nodes if n.omitted]
    constraints = [n for n in nodes if n.type == "CONSTRAINT"]

    return {
        "context_string": final_context,
        "token_breakdown": token_breakdown,
        "compression_log": compression_log,
        "metadata": metadata,
        "stats": {
            "nodes_total": len(nodes),
            "nodes_included": len(included),
            "nodes_omitted": len(omitted),
            "constraints_protected": len(constraints),
            "compression_passes": len(compression_log) - 1,
            "budget_error": error
        }
    }