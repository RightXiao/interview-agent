from __future__ import annotations

import json
from pathlib import Path

from src.agents.graph import AgentWorkflow
from src.cli.commands import HELP_TEXT, CommandType, parse_command
from src.config import AppConfig
from src.documents.exporters import export_answer_to_pdf, export_study_plan_to_pdf
from src.llm.client import OpenAICompatibleClient
from src.evaluation.dataset import load_evaluation_cases
from src.evaluation.runner import EvaluationRunner
from src.rag.indexer import VectorStore, build_local_index, import_document


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
        if command.type == CommandType.EXIT:
            return "exit"
        if command.type == CommandType.QUESTION:
            return self._handle_question(command.args[0])
        return "Unknown command. Use /help to see available commands."

    def run(self) -> None:
        print("Agent Interview Coach CLI. Type /help for commands.")
        while True:
            try:
                raw = input("> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            result = self.handle_input(raw)
            if result == "exit":
                print("Bye.")
                break
            print(result)

    def _handle_import(self, source: str) -> str:
        uploads_dir = self.base_dir / "data" / "uploads"
        target = import_document(source, uploads_dir)
        return f"Imported {target}"

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
        result = self.workflow.run(question)
        self.latest_answer = result.answer
        self.latest_sources = result.sources
        self.latest_study_plan = result.study_plan
        return result.answer

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
