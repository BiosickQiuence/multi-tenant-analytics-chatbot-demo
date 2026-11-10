import hashlib
import math
import re


def hash_embedding(text: str) -> list[float]:
    """Tiny signed token-hash vectors demonstrate plumbing, not semantic quality."""
    vector = [0.0] * 64
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = hashlib.sha256(token.encode()).digest()
        vector[int.from_bytes(digest[:2], "big") % 64] += 1 if digest[2] % 2 else -1
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else [1.0] + [0.0] * 63


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"
