from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(frozen=True)
class Conversation:
    trace_id: str
    company_name: str
    company_description: str
    conversation: str
    hint: str
    company_data: tuple
    model_answer: str
    is_hallucination: bool
    is_manipulation: bool


@dataclass(frozen=True)
class Evaluation:
    conversation_id: str
    faithfulness: int
    relevancy: int
    quality_of_interaction: int
    harmfulness: bool
    hallucination: bool
    manipulation: bool

