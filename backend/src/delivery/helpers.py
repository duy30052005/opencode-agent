import json

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

  Return ONLY valid JSON, no prose, in EXACTLY this shape:
  {{"findings": [
    {{"category": "syntax", "severity": "ok", "comment": "..."}},
    {{"category": "security", "severity": "ok", "comment": "..."}},
    {{"category": "maintainability", "severity": "ok", "comment": "..."}},
    {{"category": "coding_standards", "severity": "ok", "comment": "..."}},
    {{"category": "potential_bugs", "severity": "ok", "comment": "..."}}
  ]}}"""
# format the output
def _parse_findings(raw: str) -> list:
  text = raw.strip()
  if "```" in text:
    # drop everything upto & including the first fence
    text = text.split("```", 1)[1]
    # if it has language tag(json, python) remove it
    if text.lstrip().lower().startswith(('json', 'python')) and "\n" in text:
      text = text.split("\n",1)[1]
    #drop the closing fence and everything after it
    text = text.split("```",1)[0]
  text = text.strip()
  try:
    data = json.loads(text)
    findings = data['findings']
    if not isinstance(findings, list):
      return _failsafe()
    return findings
  except (json.JSONDecodeError, KeyError, TypeError):
    return _failsafe()

def _failsafe() -> list:
  # block delivery, never let the unreviewd code pass
  return [{'category': 'syntax', 'severity': 'critical',
           'comment': 'Review output could not be parsed'}]
