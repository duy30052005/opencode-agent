# FR-06: GitHub MCP Controlled Delivery — Implementation Plan

> Self-implementation roadmap. Owner: (you). Status: planning.
> Decision locked: **Official GitHub MCP server via Docker/stdio** + Python `mcp` SDK.

## Can this be done before FR-05?

**Yes.** FR-06 is independent of FR-05.

- **FR-05** = help the agent *understand and edit an existing codebase* (grep / LSP / replace).
- **FR-06** = *deliver* whatever code the workflow already produced (branch → commit → PR → review → approval).

FR-06 only depends on things already built: the LangGraph workflow producing `state.code`,
and the CLI (FR-04). Caveat: without FR-05 the agent ships standalone generated files rather than
patches against real repo files — fine for delivery; wire FR-05's diff/replace in later.

## How it fits the current architecture

Current flow:

```
Node1 Generator -> Node2 Executor -> Node3 Router -> (loop or END)
```

FR-06 attaches AFTER success as a delivery stage:

```
... Node3 Router -(END_SUCCESS)-> [Review Gate] -> [Human Approval] -> [MCP Delivery: branch/commit/PR]
```

**Integration point chosen:** build delivery as a separate `backend/src/delivery/` module that the
CLI/runner calls after `run_agent` returns `is_success=True`. This avoids touching the 3 existing
nodes (less merge conflict with teammates). Can be moved into the graph as `node_4_delivery` later.

---

## Phased plan

### Phase 0 — Scaffolding & config
- New package `backend/src/delivery/` with `__init__.py`.
- `.env` / `config.py` additions: `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`,
  `PROTECTED_BRANCHES=main,master,production`.
- Extend `Settings` in `config.py` (mirror the existing `GOOGLE_API_KEY` pattern).

### Phase 1 — Review Gate (FR-06.2 + FR-06.3)  ← START HERE (no MCP, offline-testable)
- `delivery/review.py` -> `run_ai_review(code, requirement) -> ReviewReport`.
- Reuse existing Gemini `llm_client` to score 5 categories: Syntax, Security, Maintainability,
  Coding Standards, Potential Bugs. Return structured JSON (severity per category + overall pass/fail).
- Any `critical` finding => gate fails => block delivery (AC-06-02).

### Phase 2 — Diff & Approval (FR-06.4 + FR-06.5)
- `delivery/diff.py` -> unified diff preview via `difflib.unified_diff`, rendered with Rich
  (reuse style of `show_code_panel`).
- `delivery/approval.py` -> human gate: show review report + diff, require `APPROVED`/`approve`.
  No git/MCP call before this returns true (AC-06-03).
- Guardrail: refuse if target branch in `PROTECTED_BRANCHES` (FR-06.5).

### Phase 3 — GitHub MCP integration (FR-06.1)  ← Official server, Docker/stdio
**Prereqs:** Docker Desktop running; GitHub PAT with `repo` + `pull_request` scopes in `.env`
as `GITHUB_TOKEN`; `pip install mcp`.

`delivery/mcp_client.py` skeleton:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm",
          "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
          "ghcr.io/github/github-mcp-server"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": settings.GITHUB_TOKEN},
)

async def deliver(...):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # tools = await session.list_tools()   # discover real tool names/args FIRST
            await session.call_tool("create_branch", {...})
            await session.call_tool("create_or_update_file", {...})  # = commit
            await session.call_tool("create_pull_request", {...})
```

Gotchas:
1. SDK is asyncio-based; CLI is sync. Wrap delivery in `asyncio.run(deliver(...))` at the CLI
   boundary — don't make the whole app async.
2. Run `session.list_tools()` once and read actual tool names/arg schemas
   (`create_branch`, `create_or_update_file`, `create_pull_request`, `get_file_contents`).
   Don't guess — print them.
3. Commit = `create_or_update_file` (commits via GitHub API). No local clone needed.
4. Keep `mcp_client.py` as dumb wrappers. The review->approval->branch->commit->PR ordering and the
   protected-branch guard live in `orchestrator.py` so they're unit-testable without Docker.
5. First `docker run` pulls the image (slow) — only affects the delivery step, not CLI startup.
   Pre-pull the image before a demo.

### Phase 4 — Audit Logging (NFR-06.1)
- `delivery/audit.py` -> append JSON lines to `audit_log.jsonl`:
  `{timestamp, action, branch, review_result, approved_by}`. Call at every stage.

### Phase 5 — CLI wiring (FR-04 touchpoint)
- Add a `deliver` flag/command in `app.py` (e.g. `MyCode run "..." --deliver`, or an interactive
  prompt after success) that calls `delivery/orchestrator.py`.

### Phase 6 — Tests
- Mock the MCP client. Assert: critical review => push blocked; no approval => no push;
  protected branch => rejected; happy path => branch+commit+PR in order; audit entries written.

## Suggested build order
Phase 1 -> Phase 2 -> Phase 4 (audit) -> Phase 3 (MCP last, behind the approval gate) -> Phase 5 -> Phase 6.
Build the offline-testable gates first so you have a demoable pipeline even if Docker misbehaves.

## Module layout
```
backend/src/delivery/
  __init__.py
  review.py         # FR-06.3 AI review (Gemini)
  diff.py           # FR-06.5 patch preview (difflib + Rich)
  approval.py       # FR-06.4 human gate + protected-branch guard
  mcp_client.py     # FR-06.1 GitHub MCP stdio wrappers
  orchestrator.py   # enforces order: review->diff->approval->branch->commit->PR
  audit.py          # NFR-06.1 audit log
```
