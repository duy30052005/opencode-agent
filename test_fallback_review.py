"""Test FallbackLLM returns valid JSON for review prompts."""
import sys
sys.path.insert(0, '.')

from src.core.llm_client import _generate_fallback_content, _is_review_prompt
from src.delivery.helpers import _parse_findings

# Simulate the actual review prompt that gets sent
sample_prompt = """You are a strict senior code reviewer. Review the Python code below
  against the requirement. Evaluate EXACTLY these 5 categories:
  syntax, security, maintainability, coding_standards, potential_bugs.
  IMPORTANT: Return ONLY a raw JSON object. No explanation, no markdown, no code fences.
  Use EXACTLY this shape:
  {"findings": [{"category": "syntax", "severity": "ok", "comment": "..."}]}"""

print("Is review prompt detected?", _is_review_prompt(sample_prompt.lower()))

raw = _generate_fallback_content(sample_prompt)
print(f"\nFallback raw output:\n{raw}\n")

findings = _parse_findings(raw)
print(f"Parsed {len(findings)} findings:")
for f in findings:
    print(f"  - [{f['severity'].upper()}] {f['category']}: {f['comment']}")

passed = not any(f['severity'] == 'critical' for f in findings)
print(f"\nReview passed: {passed}")
print("\n✅ Fix verified!" if passed else "\n❌ Fix FAILED!")
