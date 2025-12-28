from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

from config import CONVERSATIONS_PATH
from models import Conversation


def load_conversations(path: Optional[str] = None) -> List[Conversation]:
    file_path = Path(path or CONVERSATIONS_PATH)
    if not file_path.exists():
        return []

    if file_path.suffix == ".json":
        return _load_from_json(file_path)
    return []


def _load_from_json(path: Path) -> List[Conversation]:
    data = json.loads(path.read_text())
    return [
        Conversation(
            trace_id=item["trace_id"],
            company_name=item["company_name"],
            company_description=item["company_description"],
            conversation=item["conversation"],
            hint=item["hint"],
            company_data=tuple(item.get("company_data", [])),
            model_answer=item["model_answer"],
            is_hallucination=item["is_hallucination"],
            is_manipulation=item["is_manipulation"],
        )
        for item in data
    ]

