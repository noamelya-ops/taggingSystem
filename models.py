from dataclasses import dataclass


@dataclass(frozen=True)
class Conversation:
    id: str
    text: str


@dataclass(frozen=True)
class Evaluation:
    conversation_id: str
    faithfulness: int
    relevancy: int
    quality_of_interaction: int
    harmfulness: bool
    hallucination: bool
    manipulation: bool

