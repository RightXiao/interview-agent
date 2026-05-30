"""主题定义 - 颜色和样式 token"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Claude Code 风格的主题配置"""

    # 品牌色
    primary: str = "#E8A87C"  # 主色调（温暖橙色）
    secondary: str = "#85CDCA"  # 辅助色（青色）
    accent: str = "#D64045"  # 强调色（红色）

    # 文本色
    text: str = "#FAFAFA"
    text_dim: str = "#888888"
    text_muted: str = "#555555"

    # 状态色
    success: str = "#4CAF50"
    warning: str = "#FFC107"
    error: str = "#F44336"
    info: str = "#2196F3"

    # UI 元素
    border: str = "#444444"
    input_bg: str = "#2A2A2A"
    selected: str = "#3A3A3A"

    # 命令相关
    command: str = "#98C379"  # 命令名称
    command_desc: str = "#6A9955"  # 命令描述

    # Agent 相关
    agent_coordinator: str = "#C586C0"  # 协调器
    agent_explainer: str = "#4EC9B0"  # 解释者
    agent_interviewer: str = "#DCDCAA"  # 面试官
    agent_reviewer: str = "#569CD6"  # 评审员
    agent_planner: str = "#CE9178"  # 规划师

    # Markdown 渲染
    md_heading: str = "#569CD6"
    md_code: str = "#CE9178"
    md_link: str = "#9CDCFE"
    md_bold: str = "#D4D4D4"
    md_italic: str = "#C586C0"


# 默认主题实例
DEFAULT_THEME = Theme()
