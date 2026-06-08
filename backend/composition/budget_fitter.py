from backend.models.candidate import CandidateNode
from backend.composition.compressor import compress_one_level, get_content
from backend.composition.token_counter import count_tokens
from typing import List, Dict, Tuple

def build_context_string_from_blocks(blocks: Dict[int, List[CandidateNode]], user: dict, patient: dict) -> str:
    """Build the raw context string from current node states."""
    from backend.composition.block_assembler import CAPTURE_INSTRUCTION

    role_frame = f"You are assisting {user['name']}, {user['role']} — {user['department'].upper()} Department. Patient: {patient['name']}, {patient['age']}{patient['gender']}, Conditions: {', '.join(patient['conditions'])}."

    sections = []
    sections.append(f"=== ROLE ===\n{role_frame}")

    block_labels = {
        2: "GLOBAL CONSTRAINTS",
        3: "RECENT DECISIONS",
        4: "ACTIVE CONSTRAINTS",
        5: "SESSION CONTEXT",
        6: "OPEN QUESTIONS",
        7: "STALE FLAGS",
        8: "SESSION BOUNDARIES"
    }

    for block_num in [2, 3, 4, 5, 6, 7, 8]:
        nodes = blocks.get(block_num, [])

        # Skip Block 7 if empty
        if block_num == 7 and not nodes:
            continue

        # Block 8 is always the CAPTURE instruction
        if block_num == 8:
            sections.append(f"=== SESSION BOUNDARIES ===\n{CAPTURE_INSTRUCTION}")
            continue

        # Block 6 is always empty in v0.1
        if block_num == 6:
            continue

        active_nodes = [n for n in nodes if not n.omitted]
        if not active_nodes:
            continue

        label = block_labels.get(block_num, f"BLOCK {block_num}")
        block_content = f"=== {label} ===\n"
        for node in active_nodes:
            content = get_content(node)
            block_content += f"[{node.id}] {node.title}\n{content}\n\n"

        sections.append(block_content.strip())

    return "\n\n".join(sections)


def run_budget_fitter(
    blocks: Dict[int, List[CandidateNode]],
    all_nodes: List[CandidateNode],
    user: dict,
    patient: dict,
    token_budget: int = 4000,
    system_prompt_tokens: int = 800,
    user_reserve: int = 200
) -> Tuple[str, List[dict], bool]:
    """
    Iteratively compress until total fits within token_budget.
    Returns: (final_context_string, compression_log, error_flag)
    """
    available_for_context = token_budget - system_prompt_tokens - user_reserve
    compression_log = []
    error = False

    context_string = build_context_string_from_blocks(blocks, user, patient)
    context_tokens = count_tokens(context_string)
    total = system_prompt_tokens + context_tokens + user_reserve

    compression_log.append({
        "pass": 0,
        "action": "Initial count",
        "context_tokens": context_tokens,
        "total_tokens": total,
        "over_budget": total > token_budget,
        "tokens_saved": 0
    })

    pass_num = 1
    while total > token_budget:
        # Find lowest injection_weight non-CONSTRAINT node that isn't already OMIT
        candidates = [
            n for n in all_nodes
            if n.type != "CONSTRAINT" and not n.omitted
        ]

        if not candidates:
            # All non-CONSTRAINTs are omitted, still over budget
            error = True
            compression_log.append({
                "pass": pass_num,
                "action": "ERROR: CONSTRAINTs alone exceed budget",
                "context_tokens": context_tokens,
                "total_tokens": total,
                "over_budget": True,
                "tokens_saved": 0
            })
            break

        # Sort by injection_weight ascending — lowest gets compressed first
        candidates.sort(key=lambda n: n.injection_weight)
        target = candidates[0]

        tokens_before = context_tokens
        compress_one_level(target)

        context_string = build_context_string_from_blocks(blocks, user, patient)
        context_tokens = count_tokens(context_string)
        total = system_prompt_tokens + context_tokens + user_reserve
        tokens_saved = tokens_before - context_tokens

        compression_log.append({
            "pass": pass_num,
            "action": f"Compressed [{target.id}] {target.title} → {target.compression_level}",
            "node_id": target.id,
            "node_title": target.title,
            "new_level": target.compression_level,
            "context_tokens": context_tokens,
            "total_tokens": total,
            "over_budget": total > token_budget,
            "tokens_saved": tokens_saved
        })

        pass_num += 1

    return context_string, compression_log, error