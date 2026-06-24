import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_PATH = Path('audit_log.jsonl')

def log_event(action: str, branch: str ='',
              review_result: str = '', approved_by: str = 'user') -> None:
  entry = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'action': action, # review | blocked | push
    'branch': branch,
    'review_result': review_result, # passed | failed
    'approved_by': approved_by
  }
  with AUDIT_PATH.open('a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")