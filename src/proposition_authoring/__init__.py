"""ClaimGate + EvidenceGate V1 standardization apparatus."""

from .engine import AuthoringEngine
from .model import AuthoringRequest, AuthoringResult, SourceRepresentation

__all__ = ["AuthoringEngine", "AuthoringRequest", "AuthoringResult", "SourceRepresentation"]
__version__ = "1.0.0"
