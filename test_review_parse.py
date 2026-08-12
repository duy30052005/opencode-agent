"""Test _parse_findings with various LLM output formats."""
import sys
sys.path.insert(0, '.')
from src.delivery.helpers import _parse_findings, _extract_json_text

test_cases = [
    ("Clean JSON", '{"findings": [{"category": "syntax", "severity": "ok", "comment": "No issues"}, {"category": "security", "severity": "ok", "comment": "ok"}, {"category": "maintainability", "severity": "ok", "comment": "ok"}, {"category": "coding_standards", "severity": "ok", "comment": "ok"}, {"category": "potential_bugs", "severity": "ok", "comment": "ok"}]}'),
    ("Markdown fenced json", '```json\n{"findings": [{"category": "syntax", "severity": "ok", "comment": "ok"}, {"category": "security", "severity": "ok", "comment": "ok"}, {"category": "maintainability", "severity": "ok", "comment": "ok"}, {"category": "coding_standards", "severity": "ok", "comment": "ok"}, {"category": "potential_bugs", "severity": "ok", "comment": "ok"}]}\n```'),
    ("Markdown fenced no lang", '```\n{"findings": [{"category": "syntax", "severity": "ok", "comment": "ok"}]}\n```'),
    ("Prose before JSON", 'Here is my review:\n{"findings": [{"category": "syntax", "severity": "ok", "comment": "ok"}]}'),
    ("Failsafe bad JSON", 'I cannot review this code.'),
]

print("=" * 60)
all_passed = True
for name, raw in test_cases:
    findings = _parse_findings(raw)
    is_failsafe = findings[0]['comment'] == 'Review output could not be parsed'
    status = "FAILSAFE" if is_failsafe else f"OK ({len(findings)} findings)"
    print(f"  [{name}] => {status}")
    if name != "Failsafe bad JSON" and is_failsafe:
        all_passed = False
        print(f"    !! FAILED - extracted: {repr(_extract_json_text(raw)[:100])}")

print("=" * 60)
print("Result:", "ALL PASS" if all_passed else "SOME FAILED")
