"""
LSP tool contract (Phase 1)

Normalized, LLM-friendly shapes returned by core/lsp_client.py. These hide the
raw LSP payloads (0-indexed positions, integer SymbolKind enums, file:// URIs).

Conventions exposed to callers / the LLM:
- Lines and columns are 1-indexed (editor style), NOT the LSP 0-indexed values.
- File paths are project-root-relative and use forward slashes.
- `kind` is a lowercase string ("function", "class", "method", ...), not an int.
"""
from __future__ import annotations

from typing import List, Optional, TypedDict


# LSP SymbolKind (integer) -> human string.
# Spec: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolKind
SYMBOL_KIND_NAMES = {
    1: "file",
    2: "module",
    3: "namespace",
    4: "package",
    5: "class",
    6: "method",
    7: "property",
    8: "field",
    9: "constructor",
    10: "enum",
    11: "interface",
    12: "function",
    13: "variable",
    14: "constant",
    15: "string",
    16: "number",
    17: "boolean",
    18: "array",
    19: "object",
    20: "key",
    21: "null",
    22: "enum_member",
    23: "struct",
    24: "event",
    25: "operator",
    26: "type_parameter",
}


class Symbol(TypedDict):
    """One entry in a file outline (request_document_symbols)."""
    name: str
    kind: str          # mapped from SymbolKind int via SYMBOL_KIND_NAMES
    start_line: int    # 1-indexed
    end_line: int      # 1-indexed
    detail: str        # e.g. "def add", "class Calculator" ("" if unavailable)


class Location(TypedDict):
    """A definition site or a reference site."""
    file: str          # project-root-relative, forward slashes
    line: int          # 1-indexed
    col: int           # 1-indexed
    snippet: str       # the source line at `line`, stripped ("" if unreadable)


class Hover(TypedDict):
    """Signature + documentation for a symbol (request_hover)."""
    signature: str     # e.g. "def add(a, b)" ("" if unavailable)
    doc: str           # docstring / description ("" if unavailable)


class LspError(TypedDict):
    """Returned by any tool method when the LSP request fails or finds nothing.

    Callers/LLM can branch on the presence of the "error" key.
    """
    error: str


# Convenience aliases for return types.
OutlineResult = List[Symbol]
DefinitionResult = Optional[Location]
ReferencesResult = List[Location]
HoverResult = Optional[Hover]
