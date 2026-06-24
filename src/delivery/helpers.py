import json
import re
import sys

def _build_review_prompt(code: str, requirement: str) -> str:
  return f"""You are a strict senior code reviewer. Review the Python code below
  against the requirement. Evaluate EXACTLY these 5 categories:
  syntax, security, maintainability, coding_standards, potential_bugs.

  For each category assign a severity: "ok", "info", "warning", or "critical".
  Use "critical" ONLY for issues that must block delivery (e.g. code won't run,
  security hole, wrong algorithm that fails the requirement).

  Requirement: {requirement}

  Code:
  ```python
  {code}
  ```

  IMPORTANT: Return ONLY a raw JSON object. No explanation, no markdown, no code fences.
  Use EXACTLY this shape:
  {{"findings": [
    {{"category": "syntax", "severity": "ok", "comment": "..."}},
    {{"category": "security", "severity": "ok", "comment": "..."}},
    {{"category": "maintainability", "severity": "ok", "comment": "..."}},
    {{"category": "coding_standards", "severity": "ok", "comment": "..."}},
    {{"category": "potential_bugs", "severity": "ok", "comment": "..."}}
  ]}}"""

def _extract_json_text(raw: str) -> str:
  """Try multiple strategies to extract the JSON object from raw LLM output."""
  text = raw.strip()

  # Strategy 1: Strip markdown code fences (```json ... ``` or ``` ... ```)
  if "```" in text:
    inner = text.split("```", 1)[1]
    # Remove optional language tag (json, python, etc.)
    if "\n" in inner:
      first_line = inner.split("\n", 1)[0].strip().lower()
      if first_line in ('json', 'python', ''):
        inner = inner.split("\n", 1)[1]
    inner = inner.split("```", 1)[0]
    text = inner.strip()

  # Strategy 2: Find outermost { ... } block using regex
  match = re.search(r'\{[\s\S]*\}', text)
  if match:
    text = match.group(0)

  return text.strip()

def _parse_findings(raw: str) -> list:
  text = _extract_json_text(raw)
  try:
    data = json.loads(text)
    findings = data.get('findings')
    if not isinstance(findings, list) or len(findings) == 0:
      return _failsafe()
    return findings
  except (json.JSONDecodeError, KeyError, TypeError) as e:
    # Log raw output to stderr for debugging
    print(f"\n[DEBUG] Review parse failed: {e}", file=sys.stderr)
    print(f"[DEBUG] Raw LLM output:\n{raw[:500]}", file=sys.stderr)
    return _failsafe()

def _failsafe() -> list:
  # block delivery, never let the unreviewed code pass
  return [{'category': 'syntax', 'severity': 'critical',
           'comment': 'Review output could not be parsed'}]
