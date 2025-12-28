import streamlit as st

from agent import get_suggested_evaluation
from database import init_db, is_evaluated, save_evaluation
from models import Evaluation
from queue_manager import load_conversations

st.set_page_config(page_title="Recruiting AI Evaluator", layout="wide")

init_db()


def main() -> None:
    st.title("Recruiting AI Conversation Evaluator")

    if "conversations" not in st.session_state:
        st.session_state.conversations = load_conversations()
        st.session_state.current_idx = 0
        st.session_state.suggested = None

    conversations = st.session_state.conversations

    if not conversations:
        st.warning("No conversations found. Add conversations to data/conversations.json")
        return

    total = len(conversations)
    evaluated_count = sum(1 for c in conversations if is_evaluated(c.id))
    current_idx = st.session_state.current_idx
    current = conversations[current_idx]

    st.progress(evaluated_count / total, text=f"Progress: {evaluated_count}/{total} evaluated")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Conversation {current_idx + 1} of {total}")
        st.text_area("Conversation", current.text, height=300, disabled=True)

    with col2:
        if st.session_state.suggested is None or st.session_state.suggested.conversation_id != current.id:
            with st.spinner("Getting AI suggestions..."):
                st.session_state.suggested = get_suggested_evaluation(current.id, current.text)

        suggested = st.session_state.suggested

        st.subheader("Quality Ratings (1-5)")
        faithfulness = st.slider("Faithfulness", 1, 5, suggested.faithfulness, key="faith")
        relevancy = st.slider("Relevancy", 1, 5, suggested.relevancy, key="rel")
        quality = st.slider("Quality of Interaction", 1, 5, suggested.quality_of_interaction, key="qual")

        st.subheader("Guardrail Flags")

        harm_col1, harm_col2 = st.columns(2)
        with harm_col1:
            harm_true = st.button(
                "True", key="harm_t", type="primary" if suggested.harmfulness else "secondary"
            )
        with harm_col2:
            harm_false = st.button(
                "False", key="harm_f", type="primary" if not suggested.harmfulness else "secondary"
            )
        harmfulness = _resolve_toggle("harmfulness", suggested.harmfulness, harm_true, harm_false)
        st.caption(f"Harmfulness: **{harmfulness}**")

        hall_col1, hall_col2 = st.columns(2)
        with hall_col1:
            hall_true = st.button(
                "True", key="hall_t", type="primary" if suggested.hallucination else "secondary"
            )
        with hall_col2:
            hall_false = st.button(
                "False", key="hall_f", type="primary" if not suggested.hallucination else "secondary"
            )
        hallucination = _resolve_toggle("hallucination", suggested.hallucination, hall_true, hall_false)
        st.caption(f"Hallucination: **{hallucination}**")

        manip_col1, manip_col2 = st.columns(2)
        with manip_col1:
            manip_true = st.button(
                "True", key="manip_t", type="primary" if suggested.manipulation else "secondary"
            )
        with manip_col2:
            manip_false = st.button(
                "False", key="manip_f", type="primary" if not suggested.manipulation else "secondary"
            )
        manipulation = _resolve_toggle("manipulation", suggested.manipulation, manip_true, manip_false)
        st.caption(f"Manipulation: **{manipulation}**")

    st.divider()

    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

    with nav_col1:
        if st.button("← Previous", disabled=current_idx == 0):
            st.session_state.current_idx -= 1
            st.session_state.suggested = None
            st.rerun()

    with nav_col2:
        if st.button("Skip →"):
            _next_conversation(total)

    with nav_col3:
        if st.button("Save & Next →", type="primary"):
            evaluation = Evaluation(
                conversation_id=current.id,
                faithfulness=faithfulness,
                relevancy=relevancy,
                quality_of_interaction=quality,
                harmfulness=harmfulness,
                hallucination=hallucination,
                manipulation=manipulation,
            )
            save_evaluation(evaluation, current.text)
            st.success("Saved!")
            _next_conversation(total)


def _resolve_toggle(key: str, default: bool, true_clicked: bool, false_clicked: bool) -> bool:
    state_key = f"toggle_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = default
    if true_clicked:
        st.session_state[state_key] = True
    elif false_clicked:
        st.session_state[state_key] = False
    return st.session_state[state_key]


def _next_conversation(total: int) -> None:
    if st.session_state.current_idx < total - 1:
        st.session_state.current_idx += 1
        st.session_state.suggested = None
        _reset_toggles()
        st.rerun()
    else:
        st.balloons()
        st.success("All conversations evaluated!")


def _reset_toggles() -> None:
    for key in ["toggle_harmfulness", "toggle_hallucination", "toggle_manipulation"]:
        if key in st.session_state:
            del st.session_state[key]


if __name__ == "__main__":
    main()

