"""
app.py — Typer CLI app với tất cả commands cho OpenCode Agent.

Commands:
    (no subcommand)        — Interactive mode
    run  <requirement>     — Run agent với requirement cụ thể
    demo                   — Chạy một task ngẫu nhiên
    version                — Hiển thị phiên bản
    config                 — Hiển thị cấu hình hiện tại
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Prompt
from rich.text import Text

from . import __version__
from .display import (
    console,
    print_error,
    print_info,
    print_rule,
    print_success,
    print_warning,
    show_banner,
)
from .runner import run_agent
from .themes import Colors

# ──────────────────────────────────────────────────────────────────────────────
# Typer app
# ──────────────────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="opencode",
    help="OpenCode Agent -- AI-powered code generation & testing",
    add_completion=False,
    no_args_is_help=False,       # handle no-args -> interactive mode
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# ──────────────────────────────────────────────────────────────────────────────
# Sample requirements cho demo mode
# ──────────────────────────────────────────────────────────────────────────────

DEMO_REQUIREMENTS = [
    "Viết hàm tìm số nguyên tố từ 1 đến n",
    "Viết hàm tính giai thừa của n",
    "Viết hàm kiểm tra chuỗi palindrome",
    "Viết hàm tính tổng các phần tử trong list",
    "Viết hàm chia hai số a và b",
    "Viết hàm tìm ước chung lớn nhất của hai số",
    "Viết hàm kiểm tra số chẵn hay lẻ",
    "Viết hàm đảo ngược chuỗi",
    "Viết hàm tìm tổng chữ số của n",
    "Viết hàm tính số fibonacci thứ n",
    "Viết hàm sắp xếp danh sách tăng dần",
    "Viết hàm đếm số nguyên âm trong chuỗi",
]


# ──────────────────────────────────────────────────────────────────────────────
# Shared option types
# ──────────────────────────────────────────────────────────────────────────────

ModelOpt = typer.Option(
    "gemini-2.5-flash",
    "--model", "-m",
    help="LLM model to use.",
    show_default=True,
)

MaxRetriesOpt = typer.Option(
    3,
    "--max-retries", "-r",
    help="Max retry attempts when code fails.",
    min=1,
    max=10,
    show_default=True,
)

NoSaveOpt = typer.Option(
    False,
    "--no-save",
    help="Do not save state to JSON file.",
)

OutputOpt = typer.Option(
    None,
    "--output", "-o",
    help="Save final code to this file (e.g. result.py).",
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _save_code_to_file(code: str, path: str) -> None:
    try:
        Path(path).write_text(code, encoding="utf-8")
        print_success(f"Code đã được lưu → [dim]{path}[/dim]")
    except Exception as e:
        print_error(f"Không thể lưu file: {e}")


def _execute(
    requirement: str,
    model: str,
    max_retries: int,
    save_json: bool,
    output_file: Optional[str],
) -> None:
    """Thực thi agent và xử lý output file nếu cần."""
    result = run_agent(
        requirement=requirement,
        model=model,
        max_retries=max_retries,
        save_json=save_json,
    )

    # Lưu code ra file nếu được yêu cầu
    if output_file:
        code = result.get("state", {}).get("code", "")
        if code:
            _save_code_to_file(code, output_file)
        else:
            print_warning("Không có code để lưu.")


# ──────────────────────────────────────────────────────────────────────────────
# `run` command — run với requirement cụ thể
# ──────────────────────────────────────────────────────────────────────────────

@app.command("run", help="Run the agent with a specific requirement.")
def cmd_run(
    requirement: str = typer.Argument(..., help="Code requirement (use quotes if it contains spaces)."),
    model:       str  = ModelOpt,
    max_retries: int  = MaxRetriesOpt,
    no_save:     bool = NoSaveOpt,
    output:      Optional[str] = OutputOpt,
) -> None:
    show_banner(__version__)
    _execute(
        requirement=requirement,
        model=model,
        max_retries=max_retries,
        save_json=not no_save,
        output_file=output,
    )


# ──────────────────────────────────────────────────────────────────────────────
# `demo` command — random task
# ──────────────────────────────────────────────────────────────────────────────

@app.command("demo", help="Run the agent with a random demo task.")
def cmd_demo(
    model:       str  = ModelOpt,
    max_retries: int  = MaxRetriesOpt,
    no_save:     bool = NoSaveOpt,
) -> None:
    show_banner(__version__)
    req = random.choice(DEMO_REQUIREMENTS)
    console.print(
        f"  [dim]Task ngau nhien duoc chon:[/]  "
        f"[bold {Colors.PRIMARY}]{req}[/]\n"
    )
    _execute(
        requirement=req,
        model=model,
        max_retries=max_retries,
        save_json=not no_save,
        output_file=None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# `version` command
# ──────────────────────────────────────────────────────────────────────────────

@app.command("version", help="Show CLI version.")
def cmd_version() -> None:
    console.print(
        f"\n  [bold {Colors.PRIMARY}]OpenCode Agent[/]  "
        f"[dim]v{__version__}[/dim]\n"
    )


# ──────────────────────────────────────────────────────────────────────────────
# `config` command
# ──────────────────────────────────────────────────────────────────────────────

@app.command("config", help="Show current configuration.")
def cmd_config() -> None:
    import os
    from rich.table import Table
    from rich import box as rbox

    # Load settings
    try:
        from src.config import settings
        api_key = settings.GOOGLE_API_KEY
        key_display = (
            f"{api_key[:8]}{'*' * (len(api_key) - 12)}{api_key[-4:]}"
            if len(api_key) > 12 else ("***" if api_key else "[red]NOT SET[/red]")
        )
    except Exception:
        key_display = "[red]Error loading config[/red]"

    table = Table(
        title=f"[bold {Colors.PRIMARY}]⚙  Cấu Hình Hiện Tại[/]",
        box=rbox.ROUNDED,
        border_style=Colors.PRIMARY,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Key",   style=f"dim {Colors.TEXT_DIM}", width=22)
    table.add_column("Value", style=Colors.TEXT)

    table.add_row("CLI Version",        f"v{__version__}")
    table.add_row("Default Model",      "gemini-2.5-flash")
    table.add_row("Default Max Retries","3")
    table.add_row("Google API Key",     key_display)
    table.add_row("Timeout (sandbox)",  "5s")
    table.add_row("Max Output Chars",   "8,000")

    console.print()
    console.print(table)
    console.print()


# ──────────────────────────────────────────────────────────────────────────────
# Default callback — Interactive mode (no subcommand)
# ──────────────────────────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V",
        help="Show version and exit.",
        is_eager=True,
    ),
    model: str = ModelOpt,
    max_retries: int = MaxRetriesOpt,
    no_save: bool = NoSaveOpt,
    output: Optional[str] = OutputOpt,
) -> None:
    """
    OpenCode Agent -- AI-powered code generation & testing.

    Chay khong co subcommand de vao [bold]interactive mode[/bold].
    """
    if version:
        cmd_version()
        raise typer.Exit()

    # If a subcommand was invoked, don't do anything here
    if ctx.invoked_subcommand is not None:
        return

    # ─ Interactive mode ────────────────────────────────────────────────────────
    show_banner(__version__)

    console.print(
        f"  [dim {Colors.TEXT_DIM}]Chào mừng bạn đến với OpenCode Agent! "
        f"Nhập [/dim][bold {Colors.PRIMARY}]Ctrl+C[/] [dim {Colors.TEXT_DIM}]để thoát.[/dim]\n"
    )

    while True:
        try:
            # Interactive prompt
            requirement = Prompt.ask(
                Text.from_markup(f"  [bold {Colors.PRIMARY}]❯[/] [bold]Nhập yêu cầu"),
                console=console,
                default="",
            ).strip()

            if not requirement:
                print_warning("Yêu cầu không được để trống. Thử lại hoặc nhấn Ctrl+C để thoát.")
                continue

            # Special commands in interactive mode
            if requirement.lower() in ("exit", "quit", "q", "thoat", "thoat"):
                console.print(f"\n  [dim]Tam biet! Hen gap lai![/dim]\n")
                break

            if requirement.lower() in ("demo", "random"):
                requirement = random.choice(DEMO_REQUIREMENTS)
                console.print(
                    f"\n  [dim]Task ngau nhien:[/]  [bold {Colors.PRIMARY}]{requirement}[/]\n"
                )

            if requirement.lower() in ("help", "?"):
                _show_interactive_help()
                continue

            console.print()
            _execute(
                requirement=requirement,
                model=model,
                max_retries=max_retries,
                save_json=not no_save,
                output_file=output,
            )

            print_rule()
            console.print()

        except KeyboardInterrupt:
            console.print(f"\n\n  [dim]Tam biet! Hen gap lai![/dim]\n")
            break
        except typer.Exit:
            break
        except Exception as e:
            print_error(f"Lỗi không mong muốn: {e}")
            console.print_exception(show_locals=False)


def _show_interactive_help() -> None:
    from rich.table import Table
    from rich import box as rbox

    table = Table(
        box=rbox.SIMPLE,
        show_header=False,
        padding=(0, 2),
        border_style=f"dim {Colors.TEXT_MUTED}",
    )
    table.add_column("Lệnh", style=f"bold {Colors.PRIMARY}", width=12)
    table.add_column("Mô tả", style=f"dim {Colors.TEXT}")

    table.add_row("demo / random", "Chạy task ngẫu nhiên")
    table.add_row("help / ?",      "Hiển thị trợ giúp này")
    table.add_row("exit / quit",   "Thoát khỏi interactive mode")
    table.add_row("<requirement>",  "Nhập bất kỳ yêu cầu code nào")

    console.print()
    console.print(table)
    console.print()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    app()


if __name__ == "__main__":
    main()
