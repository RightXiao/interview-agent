# CLAUDE.md

本文件为 Claude Code 在此仓库中工作提供指导。

## 常用命令

```bash
# 环境准备（Python 3.11+）
pip install -e ".[dev]"
cp .env.example .env  # 填写 LLM 相关配置

# 启动交互式 CLI
python main.py

# 运行全部测试（无需真实 LLM 调用）
python -m pytest -q

# 运行单个测试文件
python -m pytest tests/test_commands.py -q

# 运行评估套件
python -m src.evaluation.run

# 在 CLI 内运行评估
# > /eval
```

## 项目架构

面向初学者的面试准备 CLI Agent，涵盖 Agent 编排、工具调用、记忆、RAG、多 Agent 协作、PDF 导入导出，全部可本地运行。

**系统流程：**

```
CLI (src/cli/app.py)
  → commands.py 解析斜杠命令（/import, /export, /eval 等）
  → 普通文本进入 AgentWorkflow.run()
    → 加载上下文（记忆 + 用户画像）
    → CoordinatorAgent.plan() 决定是否需要 RAG/规划
    → retrieve_knowledge() 基于关键词频率检索本地 JSON 索引
    → collaborate(): ExplainerAgent, InterviewerAgent, ReviewerAgent, (可选) StudyPlannerAgent
    → CoordinatorAgent.compose() 合并各部分为最终回答
    → 可选调用真实 LLM（langchain-openai ChatOpenAI）
    → 保存轮次到短期记忆，关键词匹配时更新用户画像
```

**关键架构决策：**

- `AgentWorkflow`（src/agents/graph.py）是顺序方法调用，**不是** LangGraph StateGraph。文件名和 import 虽然包含 LangGraph，但实际未使用其图执行器。
- 所有 Agent 角色（src/agents/roles.py）基于关键词匹配和模板产生**确定性**输出，不主动调用 LLM。
- RAG 检索器（src/rag/retriever.py）使用**关键词频率评分**（Counter），非向量嵌入。"向量存储"是 `data/vector_store/local_index.json`。
- PDF 导入使用 PyMuPDF（fitz），逐页提取文本并保留页码元数据用于来源引用。
- PDF 导出使用 ReportLab。中文显示需在 `.env` 中设置 `PDF_FONT_PATH` 指向中文 TTF 字体。
- 记忆分两层：`data/memory/session.json`（短期轮次，受 `MEMORY_MAX_TURNS` 限制）和 `data/memory/profile.json`（长期用户画像）。

**模块职责：**

| 模块 | 职责 |
|------|------|
| `src/cli/` | 交互循环、斜杠命令解析 |
| `src/agents/` | 工作流执行（graph.py）、Agent 角色（roles.py）、状态类型（state.py） |
| `src/tools/` | 工具注册表 — 字符串键的可调用对象，按名称可发现 |
| `src/memory/` | 基于 JSON 文件的会话 + 用户画像存储 |
| `src/rag/` | 文档分块、JSON 索引构建、关键词检索 |
| `src/documents/` | md/txt/pdf 加载、PDF 导出、数据模型 |
| `src/llm/` | OpenAI 兼容客户端封装（延迟导入 langchain-openai） |
| `src/evaluation/` | 数据集加载、指标评分、报告生成（md/json/pdf） |
| `src/config.py` | `.env` → 冻结的 `AppConfig` dataclass |

## 代码质量规范

### 通用原则

- **简洁优先**：不写多余注释，不添加当前不需要的抽象，不为假设性未来需求设计。
- **单一职责**：每个函数/类做好一件事。函数超过 50 行时考虑拆分。
- **命名清晰**：好的命名胜过注释。变量、函数、类的名称应自解释。

### Python 规范

- 遵循 PEP 8。
- 使用类型注解（type hints）标注函数签名。
- 使用 dataclass 或 Pydantic 模型定义数据结构，避免裸 dict 传递复杂数据。
- 异常处理：只在系统边界（用户输入、外部 API）做校验，内部逻辑信任调用契约。
- 字符串格式化统一使用 f-string。
- 导入顺序：标准库 → 第三方库 → 本地模块，各组之间空一行。

### 测试规范

- 测试文件放在 `tests/` 目录，命名 `test_<模块名>.py`。
- 测试必须确定性运行，不依赖真实 LLM 调用、网络请求或外部服务。
- 新功能必须附带测试，bug 修复必须附带能复现问题的回归测试。
- 运行全部测试且通过后才能提交：`python -m pytest -q`。

### 错误处理

- 不吞异常。如果捕获了异常，要么处理它，要么重新抛出并附加上下文。
- 用户面向的错误信息要清晰可操作，不要暴露内部堆栈。
- 工具调用失败时应降级到默认行为，而非中断整个工作流。

## Git 工作流

### 分支管理

- `main` 是主分支，保持可运行状态。
- 新功能从 `main` 创建功能分支：`feat/<简短描述>`。
- Bug 修复分支：`fix/<简短描述>`。
- 完成后合并回 `main`，删除功能分支。

### 提交规范

每次提交必须遵循以下格式：

```
<type>: <简短描述>

<可选的详细说明>
```

**Type 类型：**
- `feat` — 新功能
- `fix` — Bug 修复
- `refactor` — 重构（不改变外部行为）
- `test` — 添加或修改测试
- `docs` — 文档变更
- `chore` — 构建、依赖、配置等杂项

**示例：**
```
feat: 添加 StudyPlannerAgent 学习计划生成

fix: 修复 PDF 导出中文乱码问题

refactor: 将 RAG 检索逻辑从 retriever.py 提取为独立模块

test: 为 tool_registry 添加边界条件测试
```

### 提交时机

- **每个独立功能/修复完成后立即提交**，不要积攒大量改动后一次性提交。
- 提交前必须确认：
  1. 代码无语法错误
  2. 相关测试已通过：`python -m pytest -q`
  3. 不提交临时文件、缓存、`.env` 等敏感内容
- 一个提交做一件事。如果一个改动涉及多个不相关的修改，拆成多个提交。

### 提交前检查清单

```bash
# 1. 确认测试通过
python -m pytest -q

# 2. 查看改动内容
git status
git diff

# 3. 精确添加相关文件（不用 git add .）
git add src/agents/roles.py tests/test_agents.py

# 4. 提交
git commit -m "feat: 添加新的面试官角色模板"
```

### 禁止事项

- **禁止**在 `main` 分支上直接 `git reset --hard` 或 `git push --force`。
- **禁止**提交 `.env`、`__pycache__`、`.egg-info`、`data/` 等运行时生成的文件。
- **禁止**跳过测试直接提交（除非是纯文档变更）。
- **禁止**将不相关的改动合并在同一个提交中。

## 开发工作流

### 添加新功能的完整流程

```
1. 从 main 创建分支：git checkout -b feat/xxx
2. 编写代码
3. 编写测试
4. 运行测试：python -m pytest -q
5. 提交：git commit -m "feat: xxx"
6. 如有需要，重复 2-5
7. 合并回 main
```

### 修改现有代码的流程

```
1. 从 main 创建分支：git checkout -b fix/xxx 或 refactor/xxx
2. 修改代码
3. 运行现有测试确认无回归：python -m pytest -q
4. 如需要，补充新测试
5. 提交
6. 合并回 main
```
