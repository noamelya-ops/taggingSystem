import streamlit as st

from agent import get_default_evaluation, get_llm_evaluation
from database import init_db, is_evaluated, save_evaluation
from models import Evaluation
from queue_manager import load_conversations

st.set_page_config(
    page_title="Recruiting AI Evaluator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Workday-inspired professional styling - darker palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles - darker background */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #1e2a3a;
    }
    
    /* Main content area */
    .main .block-container {
        background: #1e2a3a;
        padding-top: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #60a5fa !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3, h4 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* Default text color */
    p, span, div, label {
        color: #cbd5e1 !important;
    }
    
    /* Card-like containers */
    .stExpander, [data-testid="stExpander"] {
        background: #2d3a4d;
        border-radius: 12px;
        border: 1px solid #3d4f66;
    }
    
    [data-testid="stExpander"] p, [data-testid="stExpander"] span {
        color: #e2e8f0 !important;
    }
    
    /* Info box styling */
    .stAlert {
        background: #2d3a4d;
        border-radius: 10px;
        border-left: 4px solid #60a5fa;
        color: #e2e8f0;
    }
    
    .stAlert p {
        color: #e2e8f0 !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        color: #e2e8f0 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: #3d4f66;
        border: 1px solid #4d6080;
        color: #e2e8f0 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #4d6080;
        border-color: #60a5fa;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff !important;
    }
    
    /* Slider styling */
    div[data-testid="stSlider"] {
        padding: 0.5rem 0;
    }
    
    div[data-testid="stSlider"] label {
        color: #e2e8f0 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6, #22c55e);
        border-radius: 10px;
    }
    
    .stProgress > div {
        background: #3d4f66;
    }
    
    /* Divider */
    hr {
        border-color: #3d4f66;
        margin: 1.5rem 0;
    }
    
    /* Caption text */
    .stCaption, small {
        color: #94a3b8 !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #cbd5e1;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background: #14532d;
        color: #86efac !important;
    }
    
    .stWarning {
        background: #713f12;
        color: #fde047 !important;
    }
    
    .stError {
        background: #7f1d1d;
        color: #fca5a5 !important;
    }
    
    .stInfo {
        background: #1e3a5f;
        color: #93c5fd !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        color: #60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)

init_db()

RATING_COLORS = {
    1: "#ef4444",  # Red
    2: "#f97316",  # Orange  
    3: "#eab308",  # Yellow
    4: "#84cc16",  # Light green
    5: "#22c55e",  # Green
}


def main() -> None:
    st.title("Recruiting AI Evaluator")
    st.caption("Evaluate AI assistant responses for quality and safety")

    if "conversations" not in st.session_state:
        st.session_state.conversations = load_conversations()
        st.session_state.current_idx = 0
        st.session_state.suggested = None

    conversations = st.session_state.conversations

    if not conversations:
        st.warning("No conversations found. Add conversations to data/sample_data.json")
        return

    total = len(conversations)
    evaluated_count = sum(1 for c in conversations if is_evaluated(c.trace_id))
    current_idx = st.session_state.current_idx
    current = conversations[current_idx]

    # Progress section
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.progress(evaluated_count / total)
    with col_prog2:
        st.markdown(f"<span style='color: #e2e8f0;'><strong>{evaluated_count}/{total}</strong> evaluated</span>", unsafe_allow_html=True)


    # Main layout
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(f"<p style='color: #e2e8f0;'><strong>Topic:</strong> {current.hint}</p>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='color: #e2e8f0;'>💬 Conversation</h4>", unsafe_allow_html=True)
        _render_conversation(current.conversation)
        
        st.markdown("<h4 style='color: #e2e8f0;'>Model Answer Being Evaluated</h4>", unsafe_allow_html=True)
        st.info(current.model_answer)
        
        # Company header card - moved down
        st.markdown(f"""
        <div style="background: #2d3a4d; padding: 1rem; border-radius: 12px; border: 1px solid #3d4f66; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            <div style="color: #60a5fa; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                {current.trace_id} • {current.company_name}
            </div>
            <p style="color: #94a3b8; margin: 0.25rem 0 0 0; font-size: 0.85rem;">{current.company_description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if current.company_data:
            with st.expander("Reference Data"):
                for item in current.company_data:
                    st.markdown(f"<p style='color: #e2e8f0;'><strong>Q:</strong> {item['question']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #cbd5e1;'><strong>A:</strong> {item['answer']}</p>", unsafe_allow_html=True)
                    st.markdown("<hr style='border-color: #3d4f66;'>", unsafe_allow_html=True)

    with col2:
        # Get default suggestions
        if st.session_state.suggested is None or st.session_state.suggested.conversation_id != current.trace_id:
            st.session_state.suggested = get_default_evaluation(current)
            _reset_toggles()

        suggested = st.session_state.suggested

        # LLM button
        if st.button("🤖 Ask AI", use_container_width=True):
            with st.spinner("Asking Groq AI..."):
                gemini_result, error_msg = get_llm_evaluation(current)
                if gemini_result:
                    st.session_state.suggested = gemini_result
                    # Update all sliders and toggles
                    st.session_state[f"faith_{current.trace_id}"] = gemini_result.faithfulness
                    st.session_state[f"rel_{current.trace_id}"] = gemini_result.relevancy
                    st.session_state[f"qual_{current.trace_id}"] = gemini_result.quality_of_interaction
                    st.session_state[f"toggle_harmfulness_{current.trace_id}"] = gemini_result.harmfulness
                    st.session_state[f"toggle_hallucination_{current.trace_id}"] = gemini_result.hallucination
                    st.session_state[f"toggle_manipulation_{current.trace_id}"] = gemini_result.manipulation
                    st.rerun()
                else:
                    st.error(f"Gemini API error: {error_msg}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Quality ratings card - dark
        st.markdown("""
        <div style="background: #2d3a4d; padding: 1.25rem; border-radius: 12px; border: 1px solid #3d4f66; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 0.5rem 0; color: #e2e8f0;">Quality Ratings</h4>
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">1 = Very Poor → 5 = Excellent</p>
        </div>
        """, unsafe_allow_html=True)
        
        faithfulness = _render_color_slider("Faithfulness", "faith", current.trace_id, suggested.faithfulness)
        relevancy = _render_color_slider("Relevancy", "rel", current.trace_id, suggested.relevancy)
        quality = _render_color_slider("Quality of Interaction", "qual", current.trace_id, suggested.quality_of_interaction)

        st.markdown("<hr style='border-color: #3d4f66;'>", unsafe_allow_html=True)
        
        # Guardrail flags card - dark
        st.markdown("""
        <div style="background: #2d3a4d; padding: 1.25rem; border-radius: 12px; border: 1px solid #3d4f66; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 0.5rem 0; color: #e2e8f0;">Guardrail Flags</h4>
            <p style="color: #94a3b8; font-size: 0.8rem; margin: 0;">Model predictions - verify accuracy</p>
        </div>
        """, unsafe_allow_html=True)

        harmfulness = _render_toggle_buttons("Harmfulness", "harmfulness", current.trace_id)
        hallucination = _render_toggle_buttons("Hallucination", "hallucination", current.trace_id)
        manipulation = _render_toggle_buttons("Manipulation", "manipulation", current.trace_id)

    st.markdown("<hr style='border-color: #3d4f66;'>", unsafe_allow_html=True)

    # Navigation buttons
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])

    with nav_col1:
        if st.button("← Previous", disabled=current_idx == 0, use_container_width=True):
            st.session_state.current_idx -= 1
            st.session_state.suggested = None
            _reset_toggles()
            st.rerun()

    with nav_col2:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem; color: #94a3b8;'>{current_idx + 1} of {total}</div>", unsafe_allow_html=True)

    with nav_col3:
        if st.button("Skip →", use_container_width=True):
            _next_conversation(total)

    with nav_col4:
        if st.button("Save & Next", type="primary", use_container_width=True):
            evaluation = Evaluation(
                conversation_id=current.trace_id,
                faithfulness=faithfulness,
                relevancy=relevancy,
                quality_of_interaction=quality,
                harmfulness=harmfulness,
                hallucination=hallucination,
                manipulation=manipulation,
            )
            save_evaluation(evaluation, current.conversation)
            _next_conversation(total)


def _render_color_slider(label: str, key: str, trace_id: str, default: int) -> int:
    slider_key = f"{key}_{trace_id}"
    
    # Get current value from session state or use default
    if slider_key not in st.session_state:
        st.session_state[slider_key] = default
    
    value = st.session_state[slider_key]
    color = RATING_COLORS[value]
    
    # Custom colored slider using CSS
    st.markdown(f"""
    <style>
        div[data-testid="stSlider"][data-baseweb="slider"] #{slider_key} {{
            background: linear-gradient(to right, #ef4444, #f97316, #eab308, #84cc16, #22c55e);
        }}
    </style>
    """, unsafe_allow_html=True)
    
    value = st.slider(
        label,
        min_value=1,
        max_value=5,
        value=value,
        key=slider_key,
    )
    
    # Color indicator with dark background
    color = RATING_COLORS[value]
    label_text = {1: "Very Poor", 2: "Poor", 3: "Acceptable", 4: "Good", 5: "Excellent"}[value]
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-top: -10px; margin-bottom: 15px; padding: 8px; background: {color}22; border-radius: 8px; border: 1px solid {color};">
        <div style="width: 14px; height: 14px; border-radius: 50%; background: {color}; margin-right: 8px;"></div>
        <span style="font-size: 0.85rem; color: {color}; font-weight: 500;">{label_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    return value


def _render_toggle_buttons(label: str, key: str, trace_id: str, default_value: bool = True) -> bool:
    state_key = f"toggle_{key}_{trace_id}"
    
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value
    
    current_value = st.session_state[state_key]
    
    st.markdown(f"""
    <div style="margin-bottom: 4px;">
        <span style="font-weight: 500; color: #e2e8f0;">{label}</span>
    </div>
    """, unsafe_allow_html=True)
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        true_type = "primary" if current_value else "secondary"
        if st.button("True", key=f"{key}_t_{trace_id}", type=true_type, use_container_width=True):
            st.session_state[state_key] = True
            st.rerun()
    with btn_col2:
        false_type = "primary" if not current_value else "secondary"
        if st.button("False", key=f"{key}_f_{trace_id}", type=false_type, use_container_width=True):
            st.session_state[state_key] = False
            st.rerun()
    
    return current_value


def _render_conversation(text: str) -> None:
    # Split by message boundaries, handling multi-line messages
    messages = []
    current_role = None
    current_text = []
    
    for line in text.split("\n"):
        if line.startswith("user:"):
            if current_role:
                messages.append((current_role, "\n".join(current_text)))
            current_role = "user"
            current_text = [line[5:].strip()]
        elif line.startswith("assistant:"):
            if current_role:
                messages.append((current_role, "\n".join(current_text)))
            current_role = "assistant"
            current_text = [line[10:].strip()]
        elif line.strip() and current_role:
            current_text.append(line.strip())
    
    if current_role:
        messages.append((current_role, "\n".join(current_text)))
    
    for role, content in messages:
        if role == "user":
            st.markdown(f"""
            <div style="background: #3d4f66; padding: 0.75rem 1rem; border-radius: 12px 12px 12px 4px; margin-bottom: 0.5rem; border-left: 3px solid #60a5fa;">
                <span style="color: #60a5fa; font-weight: 600; font-size: 0.8rem;">USER</span><br>
                <span style="color: #e2e8f0;">{content}</span>
            </div>
            """, unsafe_allow_html=True)
        elif role == "assistant":
            st.markdown(f"""
            <div style="background: #2d4a3d; padding: 0.75rem 1rem; border-radius: 12px 12px 4px 12px; margin-bottom: 0.5rem; border-right: 3px solid #22c55e;">
                <span style="color: #22c55e; font-weight: 600; font-size: 0.8rem;">ASSISTANT</span><br>
                <span style="color: #e2e8f0;">{content}</span>
            </div>
            """, unsafe_allow_html=True)


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
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("toggle_")]
    for key in keys_to_delete:
        del st.session_state[key]


if __name__ == "__main__":
    main()
