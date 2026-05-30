"""CLI 应用测试"""

from unittest.mock import MagicMock, patch

import pytest

from src.cli.app import InterviewApp
from src.cli.commands.base import CommandContext, CommandResult, OutputType


def test_interview_app_init(tmp_path):
    """测试 InterviewApp 初始化"""
    app = InterviewApp(base_dir=tmp_path)
    assert app.base_dir == tmp_path
    assert app.commands is not None
    assert app.renderer is not None
    assert app.session_manager is not None


def test_command_context_creation(tmp_path):
    """测试命令上下文创建"""
    app = InterviewApp(base_dir=tmp_path)
    ctx = app._create_command_context()
    assert isinstance(ctx, CommandContext)
    assert ctx.workflow is not None
    assert ctx.renderer is not None
    assert ctx.session_manager is not None


def test_process_question(tmp_path):
    """测试问题处理"""
    app = InterviewApp(base_dir=tmp_path)

    # Mock workflow
    mock_result = MagicMock()
    mock_result.answer = "Test answer"
    mock_result.sources = ["source1.md"]
    mock_result.study_plan = ""
    app.workflow = MagicMock()
    app.workflow.run.return_value = mock_result

    # 处理问题
    app._process_question("What is RAG?")

    # 验证
    assert app.latest_answer == "Test answer"
    assert app.latest_sources == ["source1.md"]
    app.workflow.run.assert_called_once_with("What is RAG?")


def test_execute_command_exit(tmp_path):
    """测试退出命令"""
    app = InterviewApp(base_dir=tmp_path)
    should_exit = app._execute_command("/exit")
    assert should_exit is True


def test_execute_command_help(tmp_path):
    """测试帮助命令"""
    app = InterviewApp(base_dir=tmp_path)
    should_exit = app._execute_command("/help")
    assert should_exit is False


def test_execute_command_unknown(tmp_path):
    """测试未知命令"""
    app = InterviewApp(base_dir=tmp_path)
    should_exit = app._execute_command("/unknown")
    assert should_exit is False


def test_session_manager(tmp_path):
    """测试会话管理"""
    from src.cli.session import SessionManager

    manager = SessionManager(tmp_path / "sessions")

    # 创建会话
    session_id = manager.create_session()
    assert session_id is not None

    # 添加轮次
    manager.add_turn(session_id, "user", "Hello")
    manager.add_turn(session_id, "assistant", "Hi there!")

    # 获取轮次
    turns = manager.get_turns(session_id)
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[1]["role"] == "assistant"

    # 列出会话
    sessions = manager.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].id == session_id


def test_command_registry():
    """测试命令注册表"""
    from src.cli.commands import CommandRegistry, create_default_registry
    from src.cli.commands.base import Command

    registry = create_default_registry()

    # 检查命令是否注册
    assert registry.get("help") is not None
    assert registry.get("exit") is not None
    assert registry.get("import") is not None
    assert registry.get("eval") is not None

    # 检查别名
    assert registry.get("h") is not None  # help 的别名
    assert registry.get("q") is not None  # exit 的别名

    # 获取所有命令
    commands = registry.get_all()
    assert len(commands) > 0

    # 获取命令名称（用于补全）
    names = registry.get_command_names()
    assert "help" in names
    assert "exit" in names
