import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import DATABASE_PATH
from models import Evaluation


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY,
                conversation_id TEXT UNIQUE,
                conversation_text TEXT,
                faithfulness INTEGER CHECK(faithfulness BETWEEN 1 AND 5),
                relevancy INTEGER CHECK(relevancy BETWEEN 1 AND 5),
                quality_of_interaction INTEGER CHECK(quality_of_interaction BETWEEN 1 AND 5),
                harmfulness BOOLEAN,
                hallucination BOOLEAN,
                manipulation BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_evaluation(evaluation: Evaluation, conversation_text: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO evaluations (
                conversation_id, conversation_text, faithfulness, relevancy,
                quality_of_interaction, harmfulness, hallucination, manipulation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evaluation.conversation_id,
                conversation_text,
                evaluation.faithfulness,
                evaluation.relevancy,
                evaluation.quality_of_interaction,
                evaluation.harmfulness,
                evaluation.hallucination,
                evaluation.manipulation,
            ),
        )
        conn.commit()


def is_evaluated(conversation_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM evaluations WHERE conversation_id = ?",
            (conversation_id,),
        )
        return cursor.fetchone() is not None


def get_all_evaluations() -> list[dict]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM evaluations ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

