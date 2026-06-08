from backend.models.candidate import CandidateNode
from typing import List, Dict

SYSTEM_PROMPT_TEMPLATE = """You are BRAHMO, an organizationally-aware AI assistant.
You have been provided with structured context from {org_name}'s knowledge graph.
This context has been filtered for {user_name}'s role ({user_role}) and permission level,
and assembled specifically for this session.

RULES:
1. Apply the organizational context below to every response.
2. CONSTRAINT nodes are non-negotiable safety rules — never suggest actions that violate them.
3. If you don't have sufficient context to answer confidently, say so rather than guessing.
4. Reference specific organizational decisions when relevant.
5. If the user shares new decisions or constraints worth remembering, note them at the end
   of your response with the prefix CAPTURE: so they can be reviewed for knowledge graph storage.

{composed_context_string}"""

CAPTURE_INSTRUCTION = """CAPTURE: If the doctor shares new decisions, clinical findings, 
or constraints during this session, note them here with the prefix CAPTURE: 
so they can be reviewed for addition to the knowledge graph."""

def assemble_blocks(nodes: List[CandidateNode], user: dict, patient: dict) -> Dict[int, List[CandidateNode]]:
    """
    Sort nodes into 8 blocks. Order is LOCKED — never change it.
    """
    blocks: Dict[int, List[CandidateNode]] = {i: [] for i in range(1, 9)}

    for node in nodes:
        # Block 2: Zone 2 global CONSTRAINTs
        if node.zone == 2 and node.type == "CONSTRAINT":
            node.block_assignment = 2
            blocks[2].append(node)

        # Block 4: Zone 1 department CONSTRAINTs
        elif node.zone == 1 and node.type == "CONSTRAINT":
            node.block_assignment = 4
            blocks[4].append(node)

        # Block 3: DECISIONs (sorted by injection weight = recency proxy)
        elif node.type == "DECISION" and node.status != "REVIEW_REQUIRED":
            node.block_assignment = 3
            blocks[3].append(node)

        # Block 7: Stale / REVIEW_REQUIRED nodes
        elif node.status == "REVIEW_REQUIRED":
            node.block_assignment = 7
            blocks[7].append(node)

        # Block 5: Everything else (FACTs, ANTI_PATTERNs, remaining DECISIONs)
        else:
            node.block_assignment = 5
            blocks[5].append(node)

    # Sort Block 3 by injection_weight descending (highest weight = most recent/important first)
    blocks[3].sort(key=lambda n: n.injection_weight, reverse=True)

    # Sort Block 5 by injection_weight descending
    blocks[5].sort(key=lambda n: n.injection_weight, reverse=True)

    return blocks