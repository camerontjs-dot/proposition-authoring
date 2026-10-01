from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Protocol

from .canonical import canonical_json, sha256_text


class SemanticBackend(Protocol):
    def proposals(self, root: dict[str, Any]) -> dict[str, list[dict[str, Any]]]: ...

    def root_frame_count(self, root_text: str, context_text: str) -> tuple[str, int, str]: ...

    def evaluate(self, candidate: dict[str, Any]) -> dict[str, Any]: ...

    def cluster_key(self, candidate: dict[str, Any]) -> str: ...


class FrozenPredecessorBackend:
    """Adapter over exact predecessor bytes fetched into vendor/frozen/.

    This adapter is a V0 convergence candidate. The vendored predecessor files remain
    independently identified research artifacts and are not silently relabeled as production.
    """

    def __init__(self, vendor_dir: str | Path = "vendor/frozen") -> None:
        root = Path(vendor_dir)
        self.proposers = self._load("pa_frozen_proposers", root / "proposers.py")
        self.authority = self._load("pa_frozen_rc1_authority", root / "evaluator.py")

    @staticmethod
    def _load(name: str, path: Path) -> ModuleType:
        if not path.exists():
            raise RuntimeError(
                f"missing frozen predecessor {path}; run scripts/fetch_frozen_predecessors.py"
            )
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def proposals(self, root: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        return {name: fn(root) for name, fn in self.proposers.PROPOSERS.items()}

    def root_frame_count(self, root_text: str, context_text: str) -> tuple[str, int, str]:
        parsed = self.authority.parse_root(root_text, context_text)
        return parsed.status, len(parsed.frames), parsed.reason

    @staticmethod
    def _clean(candidate: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in candidate.items() if k != "proposal_meta"}

    def evaluate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        return self.authority.evaluate(self._clean(candidate))

    def cluster_key(self, candidate: dict[str, Any]) -> str:
        clean = self._clean(candidate)
        frames: list[str] = []
        for child in clean["children"]:
            parsed = self.authority.parse_child(
                child["text"], clean.get("context_text", "") or ""
            )
            if parsed.status != "ok" or len(parsed.frames) != 1:
                raise RuntimeError("accepted candidate did not reparse to one child frame")
            frames.append(parsed.frames[0].key())
        return sha256_text(canonical_json(sorted(frames)))
