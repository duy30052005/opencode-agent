import json
import sys
from src.core import llm_client
from .schemas import ReviewReport, Severity
from . import helpers

# build prompt => call LLM => parse + decide
# run AI review
def run_ai_review(code: str, requirement: str) -> ReviewReport:
  prompt = helpers._build_review_prompt(code, requirement)
  raw = llm_client.llm.invoke(prompt).content

  # Debug: print raw LLM response to stderr
  print(f"\n[REVIEW DEBUG] Raw LLM response:\n{raw}\n{'='*50}", file=sys.stderr)

  findings = helpers._parse_findings(raw)
  passed = not any(f['severity'] == Severity.Critical.value for f in findings)
  return {
    'findings': findings,
    'passed': passed,
    'summary': ''
  }