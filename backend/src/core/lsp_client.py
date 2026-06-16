"""
LSP client wrapper (Phase 2)

Owns a single long-lived multilspy SyncLanguageServer session scoped to one
project root, and exposes four normalized, LLM-friendly methods:

    outline(file)                 -> list[Symbol]
    goto_definition(file, l, c)   -> Location | None
    find_references(file, l, c)   -> list[Location]
    hover(file, l, c)             -> Hover | None

All public positions are 1-indexed (editor style); this module converts to/from
the LSP 0-indexed values. All file paths in/out are project-root-relative with
forward slashes. Raw LSP shapes (URIs, integer SymbolKind, fenced markdown
hover) never escape this module.

Lifecycle (see Phase 3): start_server() has real cost (~1.4s), so the session is
opened once and held open. Use as a context manager:

    with LspClient(project_root) as lsp:
        lsp.outline("utils.py")
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from multilspy import SyncLanguageServer
from multilspy.multilspy_config import MultilspyConfig
from multilspy.multilspy_logger import MultilspyLogger

from ..schemas.lsp_schema import (
    SYMBOL_KIND_NAMES,
    DefinitionResult,
    Hover,
    HoverResult,
    Location,
    OutlineResult,
    ReferencesResult,
    Symbol,
)


class LspClient:
    """Thin, normalized facade over multilspy's SyncLanguageServer."""

    def __init__(self, project_root: str, language: str = "python") -> None:
        self.project_root = os.path.abspath(project_root)
        self.language = language
        self._config = MultilspyConfig.from_dict({"code_language": language})
        self._logger = MultilspyLogger()
        self._server = SyncLanguageServer.create(
            self._config, self._logger, self.project_root
        )
        self._ctx = None  # active start_server() context manager
        self._started = False
        self._source_cache: Dict[str, List[str]] = {}

    # ----- lifecycle -------------------------------------------------------

    def start(self) -> "LspClient":
        if not self._started:
            self._ctx = self._server.start_server()
            self._ctx.__enter__()
            self._started = True
        return self

    def stop(self) -> None:
        if self._started and self._ctx is not None:
            self._ctx.__exit__(None, None, None)
            self._ctx = None
            self._started = False
            self._source_cache.clear()

    def __enter__(self) -> "LspClient":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    def _require_started(self) -> None:
        if not self._started:
            raise RuntimeError("LspClient used before start(); call start() or use 'with'.")

    # ----- public tool methods --------------------------------------------

    def outline(self, file: str) -> OutlineResult:
        """List the top-level symbols (functions, classes, methods) in a file."""
        self._require_started()
        rel = _norm_path(file)
        try:
            raw = self._server.request_document_symbols(rel)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the node
            self._logger.log(f"outline({rel}) failed: {exc}", logging_level=40)
            return []

        symbols = _unwrap_document_symbols(raw)
        out: List[Symbol] = []
        for sym in _flatten_symbols(symbols):
            rng = sym.get("range") or sym.get("location", {}).get("range") or {}
            start = rng.get("start", {})
            end = rng.get("end", {})
            out.append(
                Symbol(
                    name=sym.get("name", ""),
                    kind=SYMBOL_KIND_NAMES.get(sym.get("kind"), str(sym.get("kind"))),
                    start_line=int(start.get("line", 0)) + 1,
                    end_line=int(end.get("line", 0)) + 1,
                    detail=sym.get("detail") or "",
                )
            )
        return out

    def goto_definition(self, file: str, line: int, col: int) -> DefinitionResult:
        """Resolve the symbol at (line, col) to its definition site (cross-file)."""
        self._require_started()
        rel = _norm_path(file)
        try:
            raw = self._server.request_definition(rel, line - 1, col - 1)
        except Exception as exc:  # noqa: BLE001
            self._logger.log(f"goto_definition({rel}) failed: {exc}", logging_level=40)
            return None

        locs = self._locations_from_raw(raw)
        return locs[0] if locs else None

    def find_references(self, file: str, line: int, col: int) -> ReferencesResult:
        """Find all usages of the symbol at (line, col) across the project."""
        self._require_started()
        rel = _norm_path(file)
        try:
            raw = self._server.request_references(rel, line - 1, col - 1)
        except Exception as exc:  # noqa: BLE001
            self._logger.log(f"find_references({rel}) failed: {exc}", logging_level=40)
            return []
        return self._locations_from_raw(raw)

    def hover(self, file: str, line: int, col: int) -> HoverResult:
        """Get the signature + documentation for the symbol at (line, col)."""
        self._require_started()
        rel = _norm_path(file)
        try:
            raw = self._server.request_hover(rel, line - 1, col - 1)
        except Exception as exc:  # noqa: BLE001
            self._logger.log(f"hover({rel}) failed: {exc}", logging_level=40)
            return None
        if not raw:
            return None
        value = (raw.get("contents") or {}).get("value", "")
        signature, doc = _parse_hover_markdown(value)
        return Hover(signature=signature, doc=doc)

    # ----- helpers ---------------------------------------------------------

    def _locations_from_raw(self, raw: Any) -> List[Location]:
        if not raw:
            return []
        items = raw if isinstance(raw, list) else [raw]
        out: List[Location] = []
        for item in items:
            rel = item.get("relativePath")
            if rel is None:
                rel = _uri_to_relpath(item.get("uri", ""), self.project_root)
            rel = _norm_path(rel)
            start = (item.get("range") or {}).get("start", {})
            line = int(start.get("line", 0)) + 1
            col = int(start.get("character", 0)) + 1
            out.append(
                Location(
                    file=rel,
                    line=line,
                    col=col,
                    snippet=self._read_line(rel, line),
                )
            )
        return out

    def _read_line(self, rel: str, line_1indexed: int) -> str:
        lines = self._source_cache.get(rel)
        if lines is None:
            abs_path = os.path.join(self.project_root, rel.replace("/", os.sep))
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
            except OSError:
                lines = []
            self._source_cache[rel] = lines
        idx = line_1indexed - 1
        if 0 <= idx < len(lines):
            return lines[idx].strip()
        return ""


# ----- module-level helpers (no LSP state) --------------------------------

def _norm_path(path: str) -> str:
    """Project-relative path with forward slashes (LSP/Windows friendly)."""
    return (path or "").replace("\\", "/").lstrip("/")


def _uri_to_relpath(uri: str, project_root: str) -> str:
    if not uri.startswith("file://"):
        return uri
    path = uri[len("file://"):]
    # Windows: file:///c:/... -> /c:/... ; strip the leading slash before drive.
    if re.match(r"^/[a-zA-Z]:", path):
        path = path[1:]
    abs_path = os.path.abspath(path)
    try:
        return os.path.relpath(abs_path, project_root).replace("\\", "/")
    except ValueError:
        return abs_path.replace("\\", "/")


def _unwrap_document_symbols(raw: Any) -> List[Dict[str, Any]]:
    # multilspy returns a (symbols, root_paths) tuple for document symbols.
    if isinstance(raw, tuple):
        raw = raw[0]
    if isinstance(raw, list):
        return raw
    return []


def _flatten_symbols(symbols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Hierarchical DocumentSymbol trees -> flat list (children inlined)."""
    flat: List[Dict[str, Any]] = []
    for sym in symbols:
        flat.append(sym)
        children = sym.get("children")
        if children:
            flat.extend(_flatten_symbols(children))
    return flat


def _parse_hover_markdown(value: str) -> tuple[str, str]:
    """Split jedi-language-server hover markdown into (signature, doc).

    Example value:
        ```python
        def add(a, b)
        ```
        ---
        Return the sum of a and b.
        **Full name:** `utils.add`
    """
    if not value:
        return "", ""

    signature = ""
    fence = re.search(r"```(?:python)?\s*\n(.*?)\n```", value, re.DOTALL)
    if fence:
        signature = fence.group(1).strip()

    # Doc = everything after the first horizontal rule, minus the "Full name" line.
    doc = ""
    if "---" in value:
        doc = value.split("---", 1)[1]
    else:
        doc = re.sub(r"```.*?```", "", value, flags=re.DOTALL)
    doc_lines = [
        ln for ln in doc.splitlines()
        if ln.strip() and not ln.strip().startswith("**Full name:**")
    ]
    return signature, "\n".join(doc_lines).strip()
