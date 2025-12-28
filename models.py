from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Conversation:
    id: str
    text: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Evaluation:
    conversation_id: str
    faithfulness: int
    relevancy: int
    quality_of_interaction: int
    harmfulness: bool
    hallucination: bool
    manipulation: bool

