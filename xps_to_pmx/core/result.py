"""Structured stage results (design doc hard constraint 4).

Every pipeline stage returns a :class:`StageResult`.  Messages carry a stable
machine ``code`` (used by tests and the JSON report), a user-facing ``text``
(Chinese, shown in the panel) and an optional ``target`` (bone / material /
object name) so the UI can offer a "locate" button.  A stage failed when it
produced at least one ``error`` message; failures are never swallowed.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

INFO = "info"
WARNING = "warning"
ERROR = "error"
LEVELS = (INFO, WARNING, ERROR)


@dataclass
class Message:
    level: str
    code: str
    text: str
    target: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.level not in LEVELS:
            raise ValueError(f"unknown message level {self.level!r}")


@dataclass
class StageResult:
    """Outcome of one pipeline stage."""

    stage: str
    messages: List[Message] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def add(self, level: str, code: str, text: str, target: str = "", **data: Any) -> Message:
        msg = Message(level, code, text, target, dict(data))
        self.messages.append(msg)
        return msg

    def info(self, code: str, text: str, target: str = "", **data: Any) -> Message:
        return self.add(INFO, code, text, target, **data)

    def warning(self, code: str, text: str, target: str = "", **data: Any) -> Message:
        return self.add(WARNING, code, text, target, **data)

    def error(self, code: str, text: str, target: str = "", **data: Any) -> Message:
        return self.add(ERROR, code, text, target, **data)

    def extend(self, other: "StageResult") -> None:
        self.messages.extend(other.messages)

    @property
    def ok(self) -> bool:
        return not any(m.level == ERROR for m in self.messages)

    def count(self, level: str) -> int:
        return sum(1 for m in self.messages if m.level == level)

    def codes(self, level: str = "") -> List[str]:
        return [m.code for m in self.messages if not level or m.level == level]

    def to_dict(self) -> Dict[str, Any]:
        return {"stage": self.stage, "ok": self.ok, "messages": [asdict(m) for m in self.messages],
                "data": self.data}

    def to_json(self, **kwargs: Any) -> str:
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("indent", 2)
        return json.dumps(self.to_dict(), **kwargs)
