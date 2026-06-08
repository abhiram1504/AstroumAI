from backend.models.candidate import CandidateNode
from typing import List

def score_nodes(nodes: List[CandidateNode]) -> List[CandidateNode]:
    """
    Nodes already have retrieval_weight and injection_weight from the DB.
    We compute a composite score for sorting within blocks.
    Higher composite = higher priority = compressed last.
    """
    for node in nodes:
        node.composite_score = (node.retrieval_weight + node.injection_weight) / 2
    return nodes