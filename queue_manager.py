import json
from pathlib import Path

from config import CONVERSATIONS_PATH
from models import Conversation


def load_conversations(path: str | None = None) -> list[Conversation]:
    file_path = Path(path or CONVERSATIONS_PATH)
    if not file_path.exists():
        return []

    if file_path.suffix == ".json":
        return _load_from_json(file_path)
    if file_path.suffix == ".csv":
        return _load_from_csv(file_path)
    return []


def _load_from_json(path: Path) -> list[Conversation]:
    data = json.loads(path.read_text())
    return [Conversation(id=item["id"], text=item["text"]) for item in data]


def _load_from_csv(path: Path) -> list[Conversation]:
    lines = path.read_text().strip().split("\n")
    if len(lines) < 2:
        return []

    conversations = []
    for line in lines[1:]:
        parts = line.split(",", 1)
        if len(parts) == 2:
            conversations.append(Conversation(id=parts[0].strip(), text=parts[1].strip()))
    return conversations

