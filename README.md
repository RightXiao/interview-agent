# Agent Interview Coach CLI

面向初学者的本地化 AI 智能体面试准备工具。通过命令行交互，直观展示智能体编排、工具调用、记忆管理、RAG 检索、多智能体协作、PDF 导入导出等核心概念。

## 核心能力

| 模块 | 说明 |
|------|------|
| LangGraph 工作流编排 | 基于 StateGraph 构建路由→检索→协作→生成的完整流程 |
| 智能 RAG 检索 | 配置 Embedding 模型时使用 ChromaDB 语义检索，未配置时自动回退到关键词匹配 |
| 工具注册与调用 | 字符串键名注册工具，智能体通过 ToolRegistry 发现并调用 |
| 双层级记忆 | 短期会话记忆（session.json）+ 长期用户画像（profile.json） |
| 多智能体协作 | Coordinator、Explainer、Interviewer、Reviewer、StudyPlanner 五个角色 |
| PDF 导入 | PyMuPDF 逐页提取文本，保留页码元数据用于来源引用 |
| PDF 导出 | ReportLab 生成答案和学习计划 PDF，支持配置中文字体 |
| 本地评估系统 | 8 个数据集案例，多维度指标，输出 md/json/pdf 三种报告 |
| 交互式 CLI | Claude Code 风格 UI：rich 渲染、prompt_toolkit 输入、Markdown 展示、Spinner 动画 |

## 快速开始

需要 Python 3.11 或更高版本。

```bash
# 安装
pip install -e ".[dev]"
cp .env.example .env
```

编辑 `.env` 配置 LLM 接入信息：

```text
LLM_BASE_URL=https://your-provider.example.com/v1
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=your-chat-model
EMBEDDING_MODEL=your-embedding-model
PDF_FONT_PATH=
```

- 仅对话功能需要 `LLM_MODEL`，不配置时使用确定性模板输出，不影响测试和评估。
- `EMBEDDING_MODEL` 启用 Chroma 向量检索，不配置时自动使用本地关键词匹配。
- `PDF_FONT_PATH` 指向中文字体 `.ttf` 文件，用于 PDF 导出的中文渲染。不设置则使用 ReportLab 内置英文字体。

## 运行

```bash
python main.py
```

### 交互式功能

- **命令面板**：输入 `/` 实时展示可用命令列表，使用上下键选择
- **Tab 补全**：输入命令前缀后按 Tab 自动补全
- **命令历史**：使用 ↑↓ 键浏览历史命令

### 可用命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示命令列表 |
| `/import path/to/file.md` | 导入文档到知识库（支持 .md / .txt / .pdf） |
| `/memory` | 查看用户画像和短期记忆 |
| `/reindex` | 重建本地知识索引 |
| `/clear` | 清空短期会话记忆 |
| `/export answer output/answer.pdf` | 导出最后一次回答为 PDF |
| `/export plan output/study_plan.pdf` | 导出最新学习计划为 PDF |
| `/eval` | 运行评估并输出报告 |
| `/exit` | 退出 |

不以 `/` 开头的输入视为普通提问，进入智能体工作流处理。

## 架构概览

```
CLI (src/cli/app.py)
  → InterviewApp 主应用类
    → InputBox (prompt_toolkit) 底部输入框，支持命令补全
    → OutputRenderer (rich) Markdown 渲染、Panel、Spinner
    → CommandRegistry 命令注册表，基于类的命令系统
    → SessionManager 会话管理（创建、恢复、轮次记录）

  命令执行流程：
    /xxx → CommandRegistry.execute() → Command.execute()
    普通文本 → AgentWorkflow.run() → Spinner + Markdown 渲染

  Agent 工作流：
    → 加载上下文（记忆 + 用户画像）
    → CoordinatorAgent.plan() 路由决策
    → retrieve_knowledge() 关键词频率检索
    → collaborate(): Explainer, Interviewer, Reviewer, (可选) StudyPlanner
    → CoordinatorAgent.compose() 整合输出
    → 可选：注入真实 LLM 优化回答
```

**模块职责：**

| 模块 | 职责 |
|------|------|
| `src/cli/` | Claude Code 风格 CLI：输入框、输出渲染、命令系统、会话管理 |
| `src/cli/ui/` | UI 组件：主题、输入框、输出渲染、Spinner、命令面板 |
| `src/cli/commands/` | 命令系统：基类、内置命令、数据命令、文档命令、评估命令 |
| `src/agents/` | LangGraph 工作流（graph.py）、智能体角色（roles.py）、状态类型（state.py） |
| `src/tools/` | 工具注册表，按名注册和调用，智能体通过它发现可用工具 |
| `src/memory/` | JSON 文件存储：会话记忆 + 用户画像 |
| `src/rag/` | 文档分块、JSON 关键词索引、检索 |
| `src/documents/` | md/txt/pdf 文档加载、PDF 导出、数据模型 |
| `src/llm/` | OpenAI 兼容接口的客户端封装（延迟导入 langchain-openai） |
| `src/evaluation/` | 数据集加载、多维指标评分、md/json/pdf 报告生成 |
| `src/config.py` | `.env` → 冻结的 AppConfig 数据类 |

**关键设计决策：**

- RAG 检索使用关键词频率评分（Counter），确保测试无需外部 API 和向量模型。
- 所有智能体角色默认输出确定性模板，不独立调用 LLM。可在 `AgentWorkflow` 注入 LLM 客户端来优化最终回答。
- 记忆分为两层：`data/memory/session.json`（短期对话，保留最近 `MEMORY_MAX_TURNS` 轮）和 `data/memory/profile.json`（长期画像）。
- ToolRegistry 保存了多个工具，智能体通过 `tools.call()` 发现和调用，而非直接调用函数。

## PDF 功能

**导入**（PyMuPDF / fitz）：
- 逐页提取文本内容
- 页码作为元数据保留，检索结果可引用来源页码
- 扫描件 PDF（无可提取文本）会返回明确错误提示，v1 不支持 OCR

**导出**（ReportLab）：
- 生成带标题、时间戳、正文、来源列表的 PDF
- 自动处理长文本换行和分页
- 中文字体通过 `PDF_FONT_PATH` 配置本地 `.ttf` 文件

## 测试

```bash
python -m pytest -q
```

共 41 个测试用例，覆盖命令系统、CLI 应用、会话管理、文档加载、PDF 导出、记忆读写、文本分块、工具注册、智能体工作流和评估流程。所有测试使用确定性行为，无需真实 LLM 调用。

## 评估系统

```bash
# 独立运行
python -m src.evaluation.run

# 或在 CLI 内运行
> /eval
```

报告输出路径：

```
evals/reports/eval_report.md
evals/reports/eval_report.json
evals/reports/eval_report.pdf
```

**8 个评估案例**覆盖：RAG 检索、工具调用、记忆管理、多智能体协作、基础知识问答、学习计划生成、中文输入、无 RAG 场景。

**评估指标**与主流评测框架对齐：

- RAGAS 风格：回答相关性、忠实度、上下文精度、上下文召回率
- DeepEval 风格：工具调用成功率、记忆命中率、多智能体完整性
- LangSmith 风格：数据集案例结构、重复执行、逐案例报告

整套评估完全本地运行，无需外部 API，适合面试演示和学习理解。
