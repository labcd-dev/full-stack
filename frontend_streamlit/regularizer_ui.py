import streamlit as st
import os
import time

# Import the core logic from your existing file
from backend_api.Regularizer.fix_syntax_error import fix_code
from backend_api.Regularizer.agents import Agents
from backend_api.Regularizer.file_management import detect_file_type


def define_upload_session_states():
    """Initializes session states required for the file upload and design process."""
    if "file_name" not in st.session_state:
        st.session_state.file_name = ""
    if "file_type" not in st.session_state:
        st.session_state.file_type = ""
    if "file_content" not in st.session_state:
        st.session_state.file_content = ""
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4o"
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "stage" not in st.session_state:
        st.session_state.stage = "upload"


def show_upload_box_with_llm(llm_options):
    """
    Displays the file uploader and LLM selector side-by-side.
    Returns True if a file is uploaded and processed into session state, False otherwise.
    """
    if st.session_state.stage == "upload":
        st.caption("Upload a system definition file to start:")
        col1, col2 = st.columns([13, 2], gap="xsmall")

        with col1:
            uploaded_file = st.file_uploader(
                "Choose a Python or MATLAB file",
                type=["py", "m"],
                accept_multiple_files=False,
                help="Only .py and .m files are allowed."
            )

        with col2:
            st.markdown('<div id="upload-selectbox-marker"></div>', unsafe_allow_html=True)
            selected_model = st.selectbox(
                "LLM Model",
                llm_options,
                index=0,
                help="Choose an LLM Model to work with."
            )
            st.session_state.model = selected_model

        # Process and save to session state if a file is uploaded
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.file_name, st.session_state.file_type = detect_file_type(uploaded_file.name)
            st.session_state.file_content = uploaded_file.getvalue().decode("utf-8")

        if __name__ == "__main__":
            st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
            # st.markdown('<div id="red_btn"></div>', unsafe_allow_html=True)
            if st.button("âš¡ï¸ Start Process", type="primary", use_container_width=True) and uploaded_file is not None:
                st.session_state.stage = "processing"
                st.session_state.edit_mode = False
                st.rerun()

    # =========================================================================
    # STAGE 2: PROCESSING
    # =========================================================================
    elif st.session_state.stage == "processing":
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.status("â³ Please wait. We found errors and we're trying to fix them...", expanded=True) as status:
            st.write("Reading source buffers...")
            st.write("Evaluating syntax and static error trees...")

            # try:
            fixed, change_applied, human_intervention = fix_code(
                st.session_state.file_content,
                model= st.session_state.model,
                file_type=st.session_state.file_type,
            )

            st.session_state.file_content = fixed
            st.session_state.change_applied = change_applied
            st.session_state.human_intervention = human_intervention

            st.session_state.stage = "result"
            st.rerun()

            # except Exception as e:
            #     status.update(label="Processing failed!", state="error")
            #     st.error(f"Error breakdown: {str(e)}")
            #     if st.button("Return to Upload"):
            #         st.session_state.stage = "upload"
            #         st.rerun()

    # =========================================================================
    # STAGE 3: RESULT PRESENTATION
    # =========================================================================
    elif st.session_state.stage == "result":
        change_applied = st.session_state.change_applied
        human_intervention = st.session_state.human_intervention

        # --- HEADERS & MESSAGES BASED ON PIPELINE OUTCOME ---
        if not change_applied:
            st.session_state.stage = "standardizing"
            st.rerun()

        st.subheader("ðŸ“Š Code Pre Processing Result")
        st.caption(f"File processed: {st.session_state.file_name}")

        if change_applied and st.session_state.file_type == "matlab":
            st.success("Your MATLAB file was successfully converted to Python. Check results and start the process.")
        elif change_applied and not human_intervention:
            st.success("âœ¨ Syntax errors successfully auto-repaired!")
        elif change_applied and human_intervention:
            st.error("âš ï¸ Something went wrong. The automated fixer was unable to completely resolve all syntax issues.")
            st.info("ðŸ’¡ The code needs a change to get fixed.")

        st.write("<br>", unsafe_allow_html=True)

        if change_applied:
            # --- DYNAMIC VIEW: CODESPAN VS TEXT AREA EDITOR ---
            if not st.session_state.edit_mode:
                # If no change was applied, preview the original input; otherwise show the fixed code
                display_code = st.session_state.file_content
                with st.container(height=500, border=True):
                    st.code(display_code, language="python")

                col1, col2, col3 = st.columns([1,3,1])
                # Action button at the bottom to alter the view layout
                with col1:
                    st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
                    if st.button("ðŸ“ Edit Code", use_container_width=True):
                        st.session_state.edit_mode = True
                        st.rerun()
                with col2:
                    st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
                    if st.button("âš¡ï¸ Continue Process", use_container_width=True):
                        st.session_state.stage = "standardizing"
                        st.rerun()
                with col3:
                    st.markdown('<div id="red_btn"></div>', unsafe_allow_html=True)
                    if st.button("ðŸ”„ Process Another File", use_container_width=True):
                        st.session_state.stage = "upload"
                        st.session_state.file_content = ""
                        st.session_state.edit_mode = False
                        st.rerun()
            else:
                # Editable layout view triggered by the button
                display_code = st.session_state.file_content

                edited_code = st.text_area(
                    "Modify your script contents directly below:",
                    value=display_code,
                    height=500,
                    key="active_code_editor"
                )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
                    if st.button("ðŸ’¾ Save Changes", type="primary", use_container_width=True):
                        st.session_state.file_content = edited_code
                        st.session_state.edit_mode = False
                        st.rerun()

                with col_cancel:
                    st.markdown('<div id="red_btn"></div>', unsafe_allow_html=True)
                    if st.button("âŒ Cancel / View Code", use_container_width=True):
                        st.session_state.edit_mode = False
                        st.rerun()

        return False

    elif st.session_state.stage == "standardizing":
        agents = Agents(st.session_state.model)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.status("â³ Please wait. We're Generating Standard Format Python File ...", expanded=True) as status:
            st.write("Reading File from input ...")
            st.write("Understanding Code Structure ...")
            st.write("Fitting Information in Standard Format ...")
            st.session_state.file_content = agents.standardize_python_file(
                st.session_state.file_content, st.session_state.selected_pipeline == "siloDesign")
        return True
def main():
    st.set_page_config(page_title="Code Syntax Auto-Fixer", layout="wide")
    llm_options = ["gpt-oss-120b", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-4o"]

    # Initialize session state variables
    define_upload_session_states()
    file_is_ready = show_upload_box_with_llm(llm_options)



if __name__ == "__main__":
    main()
