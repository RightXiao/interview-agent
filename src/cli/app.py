from __future__ import annotations

import itertools
import json
import os
import readline
import shutil
import sys
import termios
import threading
import tty
from pathlib import Path

from src.agents.graph import AgentWorkflow
from src.agents.templates import get_template, list_templates
from src.cli.commands import COMMAND_MENU, HELP_TEXT, CommandType, parse_command
from src.config import AppConfig
from src.documents.exporters import export_answer_to_pdf, export_study_plan_to_pdf
from src.llm.client import OpenAICompatibleClient
from src.evaluation.dataset import load_evaluation_cases
from src.evaluation.runner import EvaluationRunner
from src.rag.indexer import VectorStore, build_local_index, import_document


_CMD_NAMES = [cmd for cmd, _ in COMMAND_MENU]


class _Spinner:
    def __init__(self, label: str = "Thinking") -> None:
        self._label = label
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * (len(self._label) + 10) + "\r")
        sys.stdout.flush()

    def _run(self) -> None:
        spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while not self._stop_event.is_set():
            sys.stdout.write(f"\r  {next(spinner)} {self._label}...")
            sys.stdout.flush()
            self._stop_event.wait(0.1)


def _is_tty() -> bool:
    return sys.stdin.isatty()


def _read_char() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


class CliSession:
    def __init__(self, base_dir: Path | str = ".", config: AppConfig | None = None) -> None:
        self.base_dir = Path(base_dir)
        self.config = config or AppConfig.from_env(self.base_dir)
        self.store = VectorStore(
            persist_dir=self.base_dir / "data" / "vector_store",
            embedding_model=self.config.embedding_model,
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key,
        )
        llm = OpenAICompatibleClient(config=self.config) if self.config.validate_llm() == [] else None
        self.workflow = AgentWorkflow(base_dir=self.base_dir, llm=llm, top_k=self.config.rag_top_k, config=self.config)
        self.latest_answer = ""
        self.latest_sources: list[str] = []
        self.latest_study_plan = ""

    def handle_input(self, raw: str) -> str:
        command = parse_command(raw)
        if command.type == CommandType.HELP:
            return HELP_TEXT
        if command.type == CommandType.IMPORT:
            return self._handle_import(command.args[0])
        if command.type == CommandType.MEMORY:
            return self._handle_memory()
        if command.type == CommandType.REINDEX:
            return self._handle_reindex()
        if command.type == CommandType.CLEAR:
            self.workflow.memory.clear_short_term_memory()
            return "Short-term memory cleared."
        if command.type == CommandType.EXPORT_ANSWER:
            return self._handle_export_answer(command.args[0])
        if command.type == CommandType.EXPORT_PLAN:
            return self._handle_export_plan(command.args[0])
        if command.type == CommandType.EVAL:
            return self._handle_eval()
        if command.type == CommandType.SESSIONS:
            return self._handle_sessions()
        if command.type == CommandType.RESUME:
            return self._handle_resume(command.args[0])
        if command.type == CommandType.TEMPLATE:
            return self._handle_template(command.args[0] if command.args else "")
        if command.type == CommandType.EXIT:
            return "exit"
        if command.type == CommandType.QUESTION:
            return self._handle_question(command.args[0])
        return "Unknown command. Use /help to see available commands."

    # ── main loop ──────────────────────────────────────────────

    def run(self) -> None:
        history_path = self.base_dir / "data" / ".cli_history"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            readline.read_history_file(str(history_path))
        except FileNotFoundError:
            pass
        readline.set_history_length(500)

        self._print_banner()
        use_palette = _is_tty()
        while True:
            try:
                if use_palette:
                    raw = self._interactive_input()
                else:
                    raw = input("> ")
            except (EOFError, KeyboardInterrupt):
                self._save_on_exit()
                print("\nBye.")
                break
            if not raw.strip():
                continue
            result = self.handle_input(raw)
            if result == "exit":
                self._save_on_exit()
                self._print_goodbye()
                break
            print(result)

        try:
            readline.write_history_file(str(history_path))
        except OSError:
            pass

    # ── interactive input with command palette ─────────────────

    def _interactive_input(self) -> str:
        w = self._term_width()
        sys.stdout.write(f"\033[90m{'─' * w}\033[0m\r\033[90m{'─' * w}\033[0m\n")
        sys.stdout.write("\033[36m>\033[0m ")
        sys.stdout.flush()

        buf = ""
        palette_visible = False
        palette_selected = 0
        palette_lines = 0

        while True:
            ch = _read_char()

            # ── Enter ──
            if ch in ("\r", "\n"):
                if palette_visible:
                    matches = self._palette_matches(buf)
                    if matches:
                        cmd = matches[palette_selected]
                        self._clear_palette(palette_lines)
                        sys.stdout.write(f"\033[2K\r\033[36m>\033[0m {cmd}\n")
                        readline.add_history(cmd)
                        return cmd
                self._clear_palette(palette_lines)
                sys.stdout.write("\n")
                if buf.strip():
                    readline.add_history(buf)
                return buf

            # ── Escape / Arrow keys ──
            if ch == "\x1b":
                ch2 = _read_char()
                if ch2 == "[":
                    ch3 = _read_char()
                    if ch3 == "A" and palette_visible:  # Up
                        matches = self._palette_matches(buf)
                        if matches:
                            palette_selected = (palette_selected - 1) % len(matches)
                            self._redraw_palette(buf, palette_selected, palette_lines)
                    elif ch3 == "B" and palette_visible:  # Down
                        matches = self._palette_matches(buf)
                        if matches:
                            palette_selected = (palette_selected + 1) % len(matches)
                            self._redraw_palette(buf, palette_selected, palette_lines)
                    # C=Right, D=Left — ignore
                else:
                    # Bare Escape (no [) — close palette
                    if palette_visible:
                        self._clear_palette(palette_lines)
                        palette_visible = False
                        palette_lines = 0
                continue

            # ── Ctrl-C ──
            if ch == "\x03":
                self._clear_palette(palette_lines)
                sys.stdout.write("\n")
                raise KeyboardInterrupt

            # ── Ctrl-D ──
            if ch == "\x04":
                if not buf:
                    self._clear_palette(palette_lines)
                    sys.stdout.write("\n")
                    raise EOFError
                continue

            # ── Backspace ──
            if ch in ("\x7f", "\x08"):
                if buf:
                    buf = buf[:-1]
                    self._rewrite_input(buf)
                    palette_selected = 0
                    if buf.startswith("/") and len(buf) > 0:
                        matches = self._palette_matches(buf)
                        if matches:
                            palette_lines = self._draw_palette(matches, palette_selected, palette_lines)
                            palette_visible = True
                        else:
                            self._clear_palette(palette_lines)
                            palette_visible = False
                            palette_lines = 0
                    elif palette_visible:
                        self._clear_palette(palette_lines)
                        palette_visible = False
                        palette_lines = 0
                continue

            # ── Tab (cycle palette) ──
            if ch == "\t" and palette_visible:
                matches = self._palette_matches(buf)
                if matches:
                    palette_selected = (palette_selected + 1) % len(matches)
                    self._redraw_palette(buf, palette_selected, palette_lines)
                continue

            # ── Printable character ──
            if ch.isprintable():
                buf += ch
                self._rewrite_input(buf)
                palette_selected = 0

                if buf.startswith("/"):
                    matches = self._palette_matches(buf)
                    if matches:
                        palette_lines = self._draw_palette(matches, palette_selected, palette_lines)
                        palette_visible = True
                    else:
                        self._clear_palette(palette_lines)
                        palette_visible = False
                        palette_lines = 0
                elif palette_visible:
                    self._clear_palette(palette_lines)
                    palette_visible = False
                    palette_lines = 0

    def _palette_matches(self, buf: str) -> list[str]:
        if not buf:
            return []
        return [c for c in _CMD_NAMES if c.startswith(buf)]

    def _draw_palette(self, matches: list[str], selected: int, old_lines: int) -> int:
        self._clear_palette(old_lines)
        for i, cmd in enumerate(matches):
            if i == selected:
                sys.stdout.write(f"  \033[47;30m {cmd} \033[0m\n")
            else:
                sys.stdout.write(f"  \033[90m{cmd}\033[0m\n")
        sys.stdout.flush()
        return len(matches)

    def _redraw_palette(self, buf: str, selected: int, old_lines: int) -> None:
        matches = self._palette_matches(buf)
        self._clear_palette(old_lines)
        self._draw_palette(matches, selected, 0)

    def _clear_palette(self, lines: int) -> None:
        for _ in range(lines):
            sys.stdout.write("\033[A\033[2K")
        sys.stdout.flush()

    def _rewrite_input(self, buf: str) -> None:
        sys.stdout.write(f"\033[2K\r\033[36m>\033[0m {buf}")
        sys.stdout.flush()

    # ── terminal helpers ───────────────────────────────────────

    def _term_width(self) -> int:
        return shutil.get_terminal_size((80, 24)).columns

    def _print_banner(self) -> None:
        w = self._term_width()
        title = " Interview Coach "
        pad = (w - 2 - len(title)) // 2
        top = "─" * pad + title + "─" * (w - 2 - pad - len(title))
        print(f"┌{top}┐")
        print(f"│{'Type / to see commands, /exit to quit':^{w - 2}}│")
        print(f"└{'─' * (w - 2)}┘")

    def _print_goodbye(self) -> None:
        w = self._term_width()
        line = "─" * w
        print(f"\033[90m{line}\033[0m")
        print(f"{'Goodbye!':^{w}}")
        print(f"\033[90m{line}\033[0m")

    # ── command handlers ───────────────────────────────────────

    def _handle_import(self, source: str) -> str:
        uploads_dir = self.base_dir / "data" / "uploads"
        target = import_document(source, uploads_dir)
        if self.store._use_embeddings:
            try:
                count = build_local_index(
                    [self.base_dir / "data" / "knowledge_base", uploads_dir],
                    self.store,
                )
                return f"Imported {target} and indexed {count} chunks."
            except Exception as exc:
                return f"Imported {target}. Reindex failed: {exc}"
        return f"Imported {target}. No embedding model configured, skipped reindex."

    def _handle_reindex(self) -> str:
        count = build_local_index(
            [self.base_dir / "data" / "knowledge_base", self.base_dir / "data" / "uploads"],
            self.store,
        )
        return f"Reindexed {count} chunks."

    def _handle_memory(self) -> str:
        profile = self.workflow.memory.get_profile()
        turns = self.workflow.memory.get_short_term_memory()
        return json.dumps({"profile": profile, "short_term_memory": turns}, ensure_ascii=False, indent=2)

    def _handle_question(self, question: str) -> str:
        thinking = _Spinner("Thinking")
        thinking.start()
        try:
            result = self.workflow.run(question)
        finally:
            thinking.stop()
        self.latest_answer = result.answer
        self.latest_sources = result.sources
        self.latest_study_plan = result.study_plan
        return result.answer

    def _handle_sessions(self) -> str:
        sessions = self.workflow.memory.list_sessions()
        if not sessions:
            return "No saved sessions."
        lines = ["Saved sessions:"]
        for s in sessions:
            ts = s["timestamp"][:19].replace("T", " ")
            preview = s["preview"][:40] + "..." if len(s["preview"]) > 40 else s["preview"]
            lines.append(f"  {s['id']}  ({s['turn_count']} turns) {ts}  {preview}")
        return "\n".join(lines)

    def _handle_resume(self, session_id: str) -> str:
        if not self.workflow.memory.load_session(session_id):
            return f"Session '{session_id}' not found."
        return f"Resumed session '{session_id}'."

    def _handle_template(self, name: str) -> str:
        if not name:
            templates = list_templates()
            current = self.workflow.template.name if self.workflow.template else "none"
            lines = ["Available templates:", ""]
            for t in templates:
                marker = " (active)" if t.name == current else ""
                lines.append(f"  {t.name:12s} {t.label}{marker}")
                lines.append(f"               {t.description}")
            lines.append("")
            lines.append("Usage: /template <name>")
            return "\n".join(lines)
        template = get_template(name)
        if not template:
            return f"Unknown template '{name}'. Use /template to see available options."
        self.workflow.set_template(template)
        return f"Switched to template: {template.label} — {template.description}"

    def _save_on_exit(self) -> None:
        turns = self.workflow.memory.get_short_term_memory()
        if turns:
            self.workflow.memory.save_session_snapshot("auto")

    def _handle_export_answer(self, output_path: str) -> str:
        if not self.latest_answer:
            return "No answer is available yet. Ask a question before exporting."
        path = export_answer_to_pdf(
            title="Agent Interview Coach Answer",
            content=self.latest_answer,
            sources=self.latest_sources,
            output_path=self.base_dir / output_path,
            font_path=self.config.pdf_font_path,
        )
        return f"Exported answer to {path}"

    def _handle_export_plan(self, output_path: str) -> str:
        if not self.latest_study_plan:
            return "No study plan is available yet. Ask for a study plan before exporting."
        path = export_study_plan_to_pdf(
            plan=self.latest_study_plan,
            output_path=self.base_dir / output_path,
            font_path=self.config.pdf_font_path,
        )
        return f"Exported study plan to {path}"

    def _handle_eval(self) -> str:
        dataset_path = self.base_dir / "evals" / "datasets" / "interview_agent_eval.json"
        cases = load_evaluation_cases(dataset_path)
        runner = EvaluationRunner(base_dir=self.base_dir)
        report = runner.run_cases(cases)
        paths = runner.write_reports(report)
        return (
            f"Evaluation complete: {report.passed_cases}/{report.total_cases} passed. "
            f"Markdown: {paths['markdown']}; JSON: {paths['json']}; PDF: {paths['pdf']}"
        )
