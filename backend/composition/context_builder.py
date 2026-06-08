from backend.models.candidate import CandidateNode
from typing import List, Dict

def build_metadata(all_nodes: List[CandidateNode], blocks: Dict) -> dict:
    """Build per-node metadata for the frontend visualization."""
    node_details = []
    block_summary = {}

    for node in all_nodes:
        node_details.append({
            "id": node.id,
            "title": node.title,
            "type": node.type,
            "block": node.block_assignment,
            "retrieval_weight": node.retrieval_weight,
            "injection_weight": node.injection_weight,
            "distance": node.distance_from_entry,
            "zone": node.zone,
            "compression_level": node.compression_level,
            "current_tokens": node.current_tokens,
            "omitted": node.omitted,
            "reason": node.inclusion_reason,
            "status": node.status
        })

    for block_num, nodes in blocks.items():
        total_tokens = sum(n.current_tokens for n in nodes if not n.omitted)
        block_summary[block_num] = {
            "node_count": len([n for n in nodes if not n.omitted]),
            "total_tokens": total_tokens,
            "nodes": [n.id for n in nodes if not n.omitted]
        }

    return {
        "node_details": node_details,
        "block_summary": block_summary
    }