from rich.prompt import Prompt
from rich.table import Table
from rich import box
from src.cli.display import console, print_error, print_warning
from src.cli.themes import Colors
from .diff import show_diff

PROTECTED_BRANCHES = {'main','master', 'production'}
_SEV_COLOR = {
  'ok': Colors.SUCCESS, 'info': Colors.INFO,
  'warning': Colors.WARNING, 'critical': Colors.ERROR
}
def is_protected_branch(branch: str) -> bool:
  return branch.strip().lower() in PROTECTED_BRANCHES
def show_review_report(report: dict) -> None:
  table = Table(box=box.SIMPLE_HEAD,show_header=True, padding=(0,1))
  table.add_column('Category')
  table.add_column('Severity')
  table.add_column('Comment')
  for f in report['findings']:
    sev = f['severity']
    color = _SEV_COLOR.get(sev, Colors.TEXT)
    table.add_row(f['category'], f'[bold {color}]{sev}[/]', f['comment'])
  console.print(table)
  console.print()

def request_approval(report: dict, diff_text: str, target_branch: str) -> bool:
  # protect the forbidden branch
  if is_protected_branch(target_branch):
    print_error(f"Branch '{target_branch}' is protected. Use a feature branch + PR.")
    return False
  # review pass check
  show_review_report(report)
  if not report['passed']:
    print_error('AI review found a critical issue. Delivery blocked')
    return False
  # human approval
  show_diff(diff_text)
  answer = Prompt.ask(
    f" [bold {Colors.WARNING}]Type 'APPROVED' to deliver, anything else to cancel[/]",
    console=console, default='',
  ).strip()
  if answer.lower() in ("approved", "approve"):
    return True
  print_warning('Delivery cancelled - approval not given')
  return False

