# Agent Basics

An AI agent is an LLM-driven program that can observe context, decide what to do, call tools, and produce an answer. In a real project, an agent should not be only a long prompt. It should have clear state, tools, memory, and workflow boundaries.

In this project, LangGraph-style orchestration is represented by the agent workflow. The workflow loads context, retrieves knowledge, runs specialist agents, creates an answer, and saves memory.

Interview talking point: explain the agent as a workflow with state transitions, not as a single model call.

