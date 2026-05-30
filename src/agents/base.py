"""Agent 基类和消息系统"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Message:
    """Agent 间传递的消息"""

    sender: str  # 发送者名称
    receiver: str  # 接收者名称
    content: Any  # 消息内容
    msg_type: str  # 消息类型: task/result/query/response
    correlation_id: str = ""  # 关联 ID，用于匹配请求和响应

    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())[:8]


class MessageBus:
    """消息总线 - Agent 间通信的核心"""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[Message], None]]] = {}
        self._message_log: list[Message] = []

    def subscribe(self, agent_name: str, handler: Callable[[Message], None]) -> None:
        """订阅消息"""
        if agent_name not in self._handlers:
            self._handlers[agent_name] = []
        self._handlers[agent_name].append(handler)

    def publish(self, message: Message) -> None:
        """发布消息（异步）"""
        self._message_log.append(message)
        handlers = self._handlers.get(message.receiver, [])
        for handler in handlers:
            handler(message)

    def request(self, message: Message) -> Message:
        """发送请求并等待响应（同步）"""
        self._message_log.append(message)
        handlers = self._handlers.get(message.receiver, [])
        if not handlers:
            raise ValueError(f"No handler registered for {message.receiver}")

        # 调用第一个处理器
        response = None

        def capture_response(msg: Message) -> None:
            nonlocal response
            if msg.msg_type == "response" and msg.correlation_id == message.correlation_id:
                response = msg

        # 临时订阅响应
        original_handlers = self._handlers.get(message.sender, [])
        self._handlers[message.sender] = [capture_response]

        try:
            handlers[0](message)
        finally:
            # 恢复原始处理器
            if message.sender in self._handlers:
                if original_handlers:
                    self._handlers[message.sender] = original_handlers
                else:
                    del self._handlers[message.sender]

        if response is None:
            raise TimeoutError(f"No response from {message.receiver}")

        return response

    def get_message_log(self) -> list[Message]:
        """获取消息日志"""
        return self._message_log.copy()


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, llm: Any | None = None) -> None:
        self.name = name
        self.llm = llm
        self._message_bus: MessageBus | None = None

    def set_message_bus(self, bus: MessageBus) -> None:
        """设置消息总线"""
        self._message_bus = bus
        bus.subscribe(self.name, self._handle_message)

    def _handle_message(self, message: Message) -> None:
        """处理接收到的消息"""
        if message.msg_type == "task":
            result = self.execute(message.content)
            if self._message_bus and message.sender:
                response = Message(
                    sender=self.name,
                    receiver=message.sender,
                    content=result,
                    msg_type="response",
                    correlation_id=message.correlation_id,
                )
                self._message_bus.publish(response)

    def send_message(self, receiver: str, content: Any, msg_type: str = "task") -> Message | None:
        """发送消息"""
        if not self._message_bus:
            return None
        message = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            msg_type=msg_type,
        )
        self._message_bus.publish(message)
        return message

    def request_from(self, receiver: str, content: Any) -> Any:
        """向其他 Agent 请求结果"""
        if not self._message_bus:
            raise RuntimeError("MessageBus not set")
        message = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            msg_type="task",
        )
        response = self._message_bus.request(message)
        return response.content

    @abstractmethod
    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行任务，返回结果"""
        ...

    def call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        if self.llm is None:
            return ""
        try:
            return self.llm.generate(prompt)
        except Exception:
            return ""
