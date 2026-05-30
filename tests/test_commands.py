from src.cli.commands import CommandType, parse_command


def test_parse_import_command():
    command = parse_command("/import notes/rag.pdf")
    assert command.type == CommandType.IMPORT
    assert command.args == ["notes/rag.pdf"]


def test_parse_normal_question():
    command = parse_command("Explain RAG")
    assert command.type == CommandType.QUESTION
    assert command.args == ["Explain RAG"]


def test_parse_export_answer_command():
    command = parse_command("/export answer output/a.pdf")
    assert command.type == CommandType.EXPORT_ANSWER
    assert command.args == ["output/a.pdf"]


def test_parse_eval_command():
    command = parse_command("/eval")
    assert command.type == CommandType.EVAL
    assert command.args == []


def test_parse_sessions_command():
    command = parse_command("/sessions")
    assert command.type == CommandType.SESSIONS
    assert command.args == []


def test_parse_resume_command():
    command = parse_command("/resume 20260530_143022_auto")
    assert command.type == CommandType.RESUME
    assert command.args == ["20260530_143022_auto"]


def test_parse_resume_no_args():
    command = parse_command("/resume")
    assert command.type == CommandType.UNKNOWN


def test_parse_template_list():
    command = parse_command("/template")
    assert command.type == CommandType.TEMPLATE
    assert command.args == []


def test_parse_template_select():
    command = parse_command("/template bigtech")
    assert command.type == CommandType.TEMPLATE
    assert command.args == ["bigtech"]


def test_parse_menu_command():
    command = parse_command("/")
    assert command.type == CommandType.MENU
    assert command.args == []
