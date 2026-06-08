from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CandidateNode:
    id: str
    org_id: str
    type: str                    # CONSTRAINT, DECISION, ANTI_PATTERN, FACT
    title: str
    content_full: str
    content_compressed: str
    content_constraint_only: str
    importance: float
    retrieval_weight: float
    injection_weight: float
    distance_from_entry: int
    zone: int
    department: Optional[str]
    status: str
    tokens_full: int
    tokens_compressed: int
    tokens_constraint_only: int

    # These are set during composition — not from DB
    block_assignment: Optional[int] = None
    compression_level: str = "FULL"
    current_tokens: int = 0
    inclusion_reason: str = ""
    omitted: bool = False
    composite_score: float = 0.0  # Computed from retrieval_weight + injection_weight