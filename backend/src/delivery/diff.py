import difflib
from rich.syntax import Syntax
from rich.panel import Panel
from rich import box
from src.cli.display import console
from src.cli.themes import Colors

def make_diff(old_code: str, new_code: str, filename: str = 'solution.py') -> str:
  old_lines = old_code.splitlines()
  new_lines = new_code.splitlines()
  diff = difflib.unified_diff(
    old_lines, new_lines,
    fromfile=f'a/{filename}',
    tofile=f'b/{filename}',
    lineterm='',
  )
  return '\n'.join(diff)
def show_diff(diff_text: str) -> None:
  if not diff_text.strip():
    console.print(' [dim] No changes to deliver.[/dim]')
    return
  syntax = Syntax(diff_text, 'diff', theme='one-dark',
                  word_wrap= True, background_color='#1E1E2E')
  console.print(Panel(
    syntax,
    title=f'[bold {Colors.ACCENT}]± Patch Preview[/]',
    border_style=Colors.ACCENT, box= box.ROUNDED, padding=(0,1),
  ))
  console.print()