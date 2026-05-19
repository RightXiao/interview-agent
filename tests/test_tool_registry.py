from src.tools.registry import ToolRegistry


def test_tool_registry_calls_registered_tool():
    registry = ToolRegistry()
    registry.register("echo", lambda value: value)

    assert registry.call("echo", "hello") == "hello"


def test_default_tools_are_registered(tmp_path):
    registry = ToolRegistry.with_defaults(base_dir=tmp_path)

    assert registry.has("read_user_profile")
    assert registry.has("generate_study_plan")

