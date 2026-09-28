"""
memory.py
Manages per-session conversation history for multi-turn chat.
Injects the last N exchanges as context into the RAG prompt.
"""

from typing import List, Dict


class ConversationMemory:
    """Stores and retrieves chat history for multi-turn conversations."""

    def __init__(self, max_history: int = 6):
        """
        Args:
            max_history: Maximum number of past message pairs (user+assistant) to retain.
        """
        self.max_history = max_history
        self._history: List[Dict] = []  # [{"role": "user"|"assistant", "content": str}]

    def add_user(self, message: str):
        self._history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant(self, message: str):
        self._history.append({"role": "assistant", "content": message})
        self._trim()

    def _trim(self):
        """Keep only the last max_history * 2 messages."""
        max_msgs = self.max_history * 2
        if len(self._history) > max_msgs:
            self._history = self._history[-max_msgs:]

    def get_history_text(self) -> str:
        """Format history as a readable string to inject into the RAG prompt."""
        if not self._history:
            return ""
        lines = []
        for msg in self._history[:-1]:  # Exclude the current message
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        self._history = []

    def to_list(self) -> List[Dict]:
        return list(self._history)

    def __len__(self):
        return len(self._history)
