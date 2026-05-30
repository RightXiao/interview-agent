from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CommandType(str, Enum):
    HELP = "help"
    IMPORT = "import"
    MEMORY = "memory"
    REINDEX = "reindex"
    CLEAR = "clear"
    EXPORT_ANSWER = "export_answer"
    EXPORT_PLAN = "export_plan"
    EVAL = "eval"
    EXIT = "exit"
    SESSIONS = "sessions"
    RESUME = "resume"
    TEMPLATE = "template"
    QUESTION = "question"
    UNKNOWN = "unknown"


COMMAND_MENU = [
    ("/help", "Show commands"),
    ("/import <path>", "Import .md, .txt, or .pdf into uploads"),
    ("/memory", "Show user profile and short-term memory"),
    ("/reindex", "Rebuild the local knowledge index"),
    ("/clear", "Clear short-term session memory"),
    ("/export answer <path>", "Export last answer to PDF"),
    ("/export plan <path>", "Export latest study plan to PDF"),
    ("/eval", "Run evaluation and write reports"),
    ("/sessions", "List saved sessions"),
    ("/resume <id>", "Resume a saved session"),
    ("/template", "List available templates"),
    ("/template <name>", "Switch to a template"),
    ("/exit", "Exit the CLI"),
]


@dataclass(frozen=True)
class ParsedCommand:
    type: CommandType
    args: list[str]
    raw: str


def parse_command(raw: str) -> ParsedCommand:
    text = raw.strip()
    if not text:
        return ParsedCommand(CommandType.UNKNOWN, [], raw)
    if not text.startswith("/"):
        return ParsedCommand(CommandType.QUESTION, [text], raw)

    parts = text.split()
    command = parts[0].lower()
    args = parts[1:]

    if command == "/help":
        return ParsedCommand(CommandType.HELP, [], raw)
    if command == "/import":
        path = text[len("/import"):].strip()
        if path:
            return ParsedCommand(CommandType.IMPORT, [path], raw)
        return ParsedCommand(CommandType.UNKNOWN, [], "Usage: /import path/to/file.md")
    if command == "/memory":
        return ParsedCommand(CommandType.MEMORY, [], raw)
    if command == "/reindex":
        return ParsedCommand(CommandType.REINDEX, [], raw)
    if command == "/clear":
        return ParsedCommand(CommandType.CLEAR, [], raw)
    if command == "/exit":
        return ParsedCommand(CommandType.EXIT, [], raw)
    if command == "/export" and len(args) == 2 and args[0] == "answer":
        return ParsedCommand(CommandType.EXPORT_ANSWER, [args[1]], raw)
    if command == "/export" and len(args) == 2 and args[0] == "plan":
        return ParsedCommand(CommandType.EXPORT_PLAN, [args[1]], raw)
    if command == "/eval":
        return ParsedCommand(CommandType.EVAL, [], raw)
    if command == "/sessions":
        return ParsedCommand(CommandType.SESSIONS, [], raw)
    if command == "/resume":
        session_id = text[len("/resume"):].strip()
        if session_id:
            return ParsedCommand(CommandType.RESUME, [session_id], raw)
        return ParsedCommand(CommandType.UNKNOWN, [], "Usage: /resume <session_id>")
    if command == "/template":
        name = text[len("/template"):].strip()
        if name:
            return ParsedCommand(CommandType.TEMPLATE, [name], raw)
        return ParsedCommand(CommandType.TEMPLATE, [], raw)
    return ParsedCommand(CommandType.UNKNOWN, args, raw)


HELP_TEXT = """Commands:
/help                         Show commands
/import path/to/file.md        Import .md, .txt, or .pdf into uploads
/memory                       Show user profile and short-term memory
/reindex                      Rebuild the local knowledge index
/clear                        Clear short-term session memory
/export answer output/a.pdf    Export last answer to PDF
/export plan output/plan.pdf   Export latest study plan to PDF
/eval                         Run evaluation and write reports
/sessions                     List saved sessions
/resume <session_id>          Resume a saved session
/template                     List available templates
/template <name>              Switch to a template (bigtech/soe/foreign/unicorn/boutique)
/exit                         Exit the CLI
"""
