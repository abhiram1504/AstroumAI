from backend.models.candidate import CandidateNode

def assign_initial_compression(node: CandidateNode) -> CandidateNode:
    """
    Assign compression level based on distance.
    CONSTRAINT nodes are ALWAYS FULL, no matter what.
    """
    if node.type == "CONSTRAINT":
        node.compression_level = "FULL"
        node.current_tokens = node.tokens_full
        node.inclusion_reason = "CONSTRAINT — always full"
        return node

    if node.distance_from_entry <= 1:
        node.compression_level = "FULL"
        node.current_tokens = node.tokens_full
        node.inclusion_reason = f"Distance {node.distance_from_entry} — full content"
    elif node.distance_from_entry == 2:
        node.compression_level = "COMPRESSED"
        node.current_tokens = node.tokens_compressed
        node.inclusion_reason = f"Distance {node.distance_from_entry} — compressed"
    else:
        node.compression_level = "CONSTRAINT_ONLY"
        node.current_tokens = node.tokens_constraint_only
        node.inclusion_reason = f"Distance {node.distance_from_entry} — constraint only"

    return node

def get_content(node: CandidateNode) -> str:
    """Return the right content string based on current compression level."""
    if node.omitted:
        return ""
    if node.compression_level == "FULL":
        return node.content_full
    elif node.compression_level == "COMPRESSED":
        return node.content_compressed
    elif node.compression_level == "CONSTRAINT_ONLY":
        return node.content_constraint_only
    return ""

def compress_one_level(node: CandidateNode) -> bool:
    """
    Push node down one compression level.
    Returns True if it was compressed, False if already at OMIT.
    NEVER call this on CONSTRAINT nodes.
    """
    if node.type == "CONSTRAINT":
        return False  # Safety guard

    if node.compression_level == "FULL":
        node.compression_level = "COMPRESSED"
        node.current_tokens = node.tokens_compressed
        node.inclusion_reason += " → compressed by budget fitter"
        return True
    elif node.compression_level == "COMPRESSED":
        node.compression_level = "CONSTRAINT_ONLY"
        node.current_tokens = node.tokens_constraint_only
        node.inclusion_reason += " → constraint_only by budget fitter"
        return True
    elif node.compression_level == "CONSTRAINT_ONLY":
        node.compression_level = "OMIT"
        node.current_tokens = 0
        node.omitted = True
        node.inclusion_reason += " → omitted by budget fitter"
        return True
    return False  # Already OMIT