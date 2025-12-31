import streamlit as st


def create_button_column(button, col_index: int, columns):
    """Create a button in a specific column and handle its action."""
    with columns[col_index]:
        return st.button(button["label"], use_container_width=True, key=button["key"])


def create_navigation_button(button_info: dict) -> bool:
    """Create a navigation button with a message."""
    if st.button(button_info["label"], use_container_width=True, key=button_info["key"]):
        st.session_state.messages.append({
            "role": button_info.get("role", "assistant"),
            "content": button_info["content"]
        })
        st.session_state.guided_flow_active = button_info.get("flow_active", False)
        st.session_state.conversation_mode = button_info.get("mode", "chat")
        st.rerun()
        return True
    return False


def create_step_navigation_button(step_name: str) -> bool:
    """Create a button that navigates to a specific step."""
    if st.button(step_name, use_container_width=True):
        st.session_state.messages.append({
            "role": "user",
            "content": step_name
        })
        return True
    return False


def create_message_with_link(content: str) -> None:
    """Display a message with a link."""
    st.markdown(content, unsafe_allow_html=True)


def render_root_options():
    """Render the root/landing options for guided flow."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Legal Document Support", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Legal Document Support"
            })
            st.session_state.guided_step = "legal"
            st.rerun()
    
    with col2:
        if st.button("Bereavement Support", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Bereavement Support"
            })
            st.session_state.guided_step = "breavement"
            st.rerun()
    
    with col3:
        if st.button("Final Wishes Support", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Final Wishes Support"
            })
            st.session_state.guided_step = "final_wishes"
            st.rerun()


def render_final_wishes_options():
    """Render Final Wishes support options."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="large")
    
    options = [
        {
            "col": col1,
            "label": "My Documents",
            "key": "final_wishes_my_documents",
            "content": "👉 [Click here to check Your Documents](https://trustinheritance.toolboxx.co.uk/mydigifile)"
        },
        {
            "col": col2,
            "label": "Personal Messages",
            "key": "final_wishes_personal_messages",
            "content": "👉 [Click here to check your Personal Messages](https://trustinheritance.toolboxx.co.uk/payment/personal-message)"
        },
        {
            "col": col3,
            "label": "Funeral Wishes",
            "key": "final_wishes_funeral_wishes",
            "content": "👉 [Click here to check your Funeral Wishes](https://trustinheritance.toolboxx.co.uk/payment/what-to-do-when-planning-your-funeral)"
        },
        {
            "col": col4,
            "label": "My Digital Legacy",
            "key": "final_wishes_digital_legacy",
            "content": "👉 [Click here for Full Estate Administration](https://trustinheritance.toolboxx.co.uk/payment/digital-assets)"
        },
        {
            "col": col5,
            "label": "Trusted People",
            "key": "final_wishes_trusted_people",
            "content": "👉 [Click here to add your Trusted People](https://trustinheritance.toolboxx.co.uk/profile#tab-trusted)"
        },
        {
            "col": col6,
            "label": "Nags",
            "key": "final_wishes_nags",
            "content": "👉 [Click here to check your Nags](https://trustinheritance.toolboxx.co.uk/nags)"
        }
    ]
    
    for option in options:
        with option["col"]:
            if st.button(option["label"], use_container_width=True, key=option["key"]):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": option["content"]
                })
                st.session_state.guided_flow_active = False
                st.session_state.conversation_mode = "chat"
                st.rerun()


def render_bereavement_options():
    """Render Bereavement support options."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5, gap="large")
    
    options = [
        {
            "col": col1,
            "label": "A Little Help",
            "key": "bereavement_little_help",
            "content": "👉 [Click here to check Bereavement Guide](https://trustinheritance.toolboxx.co.uk/holder/10-steps)"
        },
        {
            "col": col2,
            "label": "A Little More Help",
            "key": "bereavement_more_help",
            "content": "👉 [Click here to check our Executor Toolkit](https://trustinheritance.toolboxx.co.uk/what-to-do-when-someone-dies/2808/questionnaire/step/11)"
        },
        {
            "col": col3,
            "label": "Lots of Help",
            "key": "bereavement_lots_help",
            "content": "👉 [Click here to check Executor Toolkit Plus](https://trustinheritance.toolboxx.co.uk/payment/executor-toolkit-plus/5175)"
        },
        {
            "col": col4,
            "label": "Hand It All Over",
            "key": "bereavement_hand_over",
            "content": "👉 [Click here for Full Estate Administration](https://trustinheritance.toolboxx.co.uk/estate-administration)"
        },
        {
            "col": col5,
            "label": "Online Grief Support",
            "key": "bereavement_grief_support",
            "content": "👉 [Click here for Online Grief Support](https://trustinheritance.toolboxx.co.uk/grief-support)"
        }
    ]
    
    for option in options:
        with option["col"]:
            if st.button(option["label"], use_container_width=True, key=option["key"]):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": option["content"]
                })
                st.session_state.guided_flow_active = False
                st.session_state.conversation_mode = "chat"
                st.rerun()


def render_legal_options():
    """Render Legal Document support options."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        if st.button("Will Writing", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Will Writing"
            })
            st.session_state.guided_step = "will_mode"
            st.rerun()
    
    with col2:
        if st.button("Living Will", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "👉 [Click here to start your Living Will](https://trustinheritance.toolboxx.co.uk/living-will/5999/questionnaire/step/2)"
            })
            st.session_state.guided_flow_active = False
            st.session_state.conversation_mode = "chat"
            st.rerun()
    
    with col3:
        if st.button("Lasting Power of Attorney (LPA)", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": "Lasting Power of Attorney (LPA)"
            })
            st.session_state.guided_step = "lpa_mode"
            st.rerun()


def render_lpa_mode_options():
    """Render LPA (Lasting Power of Attorney) mode options."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### LPA Options")
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    options = [
        {
            "col": col1,
            "label": "Online",
            "content": "👉 [Click here to start writing your LPA](https://trustinheritance.toolboxx.co.uk/select-lpa)"
        },
        {
            "col": col2,
            "label": "Telephone",
            "content": "Telephone-based LPA support is available."
        },
        {
            "col": col3,
            "label": "Video",
            "content": "Video-based LPA support is available."
        }
    ]
    
    for option in options:
        with option["col"]:
            if st.button(option["label"], use_container_width=True):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": option["content"]
                })
                st.session_state.guided_flow_active = False
                st.session_state.conversation_mode = "chat"
                st.rerun()


def render_will_mode_options():
    """Render Will Writing mode options."""
    st.markdown("### Will Writing Options")
    col1, col2, col3 = st.columns(3)
    
    options = [
        {
            "col": col1,
            "label": "Online",
            "content": "👉 [Click here to start writing your will](https://trustinheritance.toolboxx.co.uk/select-will)"
        },
        {
            "col": col2,
            "label": "Telephone",
            "content": "Telephone-based will writing support is available."
        },
        {
            "col": col3,
            "label": "Video",
            "content": "Video-based will writing support is available."
        }
    ]
    
    for option in options:
        with option["col"]:
            if st.button(option["label"], use_container_width=True):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": option["content"]
                })
                st.session_state.guided_flow_active = False
                st.rerun()

