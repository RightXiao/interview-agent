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

