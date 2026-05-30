"""命令系统测试"""

from src.cli.commands import create_default_registry
from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


def test_command_registry_creation():
    """测试命令注册表创建"""
    registry = create_default_registry()
    commands = registry.get_all()
    assert len(commands) > 0


def test_help_command_exists():
    """测试 help 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("help")
    assert cmd is not None
    assert cmd.name == "help"
    assert "h" in cmd.aliases
    assert "?" in cmd.aliases


def test_exit_command_exists():
    """测试 exit 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("exit")
    assert cmd is not None
    assert cmd.name == "exit"
    assert "q" in cmd.aliases


def test_import_command_exists():
    """测试 import 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("import")
    assert cmd is not None
    assert cmd.name == "import"
    assert "i" in cmd.aliases


def test_export_command_exists():
    """测试 export 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("export")
    assert cmd is not None
    assert cmd.name == "export"


def test_eval_command_exists():
    """测试 eval 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("eval")
    assert cmd is not None
    assert cmd.name == "eval"


def test_memory_command_exists():
    """测试 memory 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("memory")
    assert cmd is not None
    assert cmd.name == "memory"


def test_sessions_command_exists():
    """测试 sessions 命令存在"""
    registry = create_default_registry()
    cmd = registry.get("sessions")
    assert cmd is not None
    assert cmd.name == "sessions"


def test_command_alias_resolution():
    """测试命令别名解析"""
    registry = create_default_registry()

    # 通过别名获取命令
    cmd = registry.get("h")
    assert cmd is not None
    assert cmd.name == "help"

    cmd = registry.get("q")
    assert cmd is not None
    assert cmd.name == "exit"

    cmd = registry.get("i")
    assert cmd is not None
    assert cmd.name == "import"


def test_command_execution_help():
    """测试 help 命令执行"""
    registry = create_default_registry()
    cmd = registry.get("help")

    # 创建带 _command_registry 的模拟上下文
    ctx = CommandContext()
    ctx._command_registry = registry

    # 执行命令
    result = cmd.execute("", ctx)

    assert isinstance(result, CommandResult)
    assert result.success is True
    assert result.output_type == OutputType.MARKDOWN


def test_command_execution_exit():
    """测试 exit 命令执行"""
    registry = create_default_registry()
    cmd = registry.get("exit")

    # 创建模拟上下文
    ctx = CommandContext()

    # 执行命令
    result = cmd.execute("", ctx)

    assert isinstance(result, CommandResult)
    assert result.success is True
    assert result.data.get("action") == "exit"


def test_command_execution_unknown():
    """测试未知命令执行"""
    registry = create_default_registry()

    # 创建模拟上下文
    ctx = CommandContext()

    # 执行未知命令
    result = registry.execute("/unknown", ctx)

    assert isinstance(result, CommandResult)
    assert result.success is False


def test_command_execution_import_no_args():
    """测试 import 命令无参数"""
    registry = create_default_registry()
    cmd = registry.get("import")

    # 创建模拟上下文
    ctx = CommandContext()

    # 执行命令
    result = cmd.execute("", ctx)

    assert isinstance(result, CommandResult)
    assert result.success is False


def test_command_completion():
    """测试命令补全"""
    registry = create_default_registry()
    names = registry.get_command_names()

    # 检查命令名称
    assert "help" in names
    assert "exit" in names
    assert "import" in names
    assert "export" in names
    assert "eval" in names
    assert "memory" in names
    assert "sessions" in names
    assert "resume" in names
    assert "template" in names
    assert "reindex" in names
    assert "clear" in names
    assert "model" in names
