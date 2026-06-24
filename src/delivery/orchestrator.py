from .review import run_ai_review
from .diff import make_diff
from .approval import request_approval
from datetime import datetime, timezone
from . import mcp_client
from . import audit
from . import auth

def deliver(code: str, requirement: str,
            target_branch = None,
            filename: str = 'solution.py',
            old_code: str = '') -> bool:
  if target_branch is None:
          target_branch = f"feature/agent-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
  # AI review
  report = run_ai_review(code,requirement)
  result = 'passed' if report['passed'] else 'failed'
  audit.log_event('review', branch=target_branch, review_result= result)

  #build diff
  diff_text = make_diff(old_code, code, filename)

  # review pass + branch review + human approval
  if not request_approval(report, diff_text, target_branch):
    audit.log_event('blocked', branch=target_branch,review_result=result)
    return False
  
  # delivery - stub now , real mcp later
  _deliver_via_mcp(code, filename, target_branch)
  audit.log_event('push', branch= target_branch, review_result= 'passed')
  return True
def _deliver_via_mcp(code: str, filename: str, target_branch: str):
  token = auth.get_user_token()
  pr_url = mcp_client.deliver_via_mcp(
    token=token,
    branch=target_branch, path=filename, content=code,
    title=f"OpenCode Agent: {filename}",
    body="Automated delivery, reviewed & approved via the agent gate.",
  )
  print(f"PR created: {pr_url}")
