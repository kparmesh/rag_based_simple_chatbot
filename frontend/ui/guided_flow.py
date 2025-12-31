import streamlit as st
from ui.components import (
    render_root_options,
    render_final_wishes_options,
    render_bereavement_options,
    render_legal_options,
    render_lpa_mode_options,
    render_will_mode_options,
)


# Guided flow step mapping
GUIDED_FLOW_STEPS = {
    "root": render_root_options,
    "final_wishes": render_final_wishes_options,
    "breavement": render_bereavement_options,
    "legal": render_legal_options,
    "lpa_mode": render_lpa_mode_options,
    "will_mode": render_will_mode_options,
}


def render_guided_flow():
    """Render the guided flow based on current step."""
    if not st.session_state.guided_flow_active:
        return
    
    current_step = st.session_state.guided_step
    
    # Get the appropriate render function for the current step
    render_function = GUIDED_FLOW_STEPS.get(current_step)
    
    if render_function:
        render_function()
    else:
        # Default to root if step is unknown
        st.session_state.guided_step = "root"
        render_root_options()

