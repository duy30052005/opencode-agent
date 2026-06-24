import json
from src.core import llm_client
from .schemas import ReviewReport, Severity
from . import helpers

# build prompt => call LLM => parse + decide
#run AI review 
def run_ai_review(code: str, requirement: str) -> ReviewReport:
  prompt = helpers._build_review_prompt(code, requirement)
  raw = llm_client.llm.invoke(prompt).content
  findings = helpers._parse_findings(raw)
  passed = not any(f['severity'] == Severity.Critical.value for f in findings)
  return {
    'findings': findings,
    'passed': passed,
    'summary': ''
  }