import streamlit as st
from auth.auth_handler import create_user, authenticate_user, get_job_titles, DEPARTMENTS
import bcrypt

def show_login_page():
    st.title("🔐 Login to Waste Management Dashboard")

    # Handle 2FA verification if needed
    if 'awaiting_2fa' in st.session_state:
        show_2fa_verification()
        return

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True)
        with col2:
            if st.form_submit_button("Forgot Password?", use_container_width=True):
                st.session_state['show_password_reset'] = True
                st.rerun()

        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                # First authentication step
                auth_result = authenticate_user(username, password)

                if auth_result == "2FA_REQUIRED":
                    # Store username for 2FA step
                    st.session_state['awaiting_2fa'] = True
                    st.session_state['2fa_username'] = username
                    st.session_state['2fa_password'] = password
                    st.rerun()
                elif auth_result:
                    st.session_state['user'] = auth_result
                    st.session_state['authenticated'] = True
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_2fa_verification():
    st.subheader("Two-Factor Authentication")
    st.info("Please enter the verification code from your authenticator app")

    with st.form("2fa_form"):
        verification_code = st.text_input("Verification Code", max_chars=6)

        if st.form_submit_button("Verify"):
            if not verification_code:
                st.error("Please enter the verification code")
            else:
                # Complete authentication with 2FA
                username = st.session_state['2fa_username']
                password = st.session_state['2fa_password']

                user = authenticate_user(username, password, verification_code)

                if user and user != "2FA_REQUIRED":
                    # Authentication successful
                    st.session_state['user'] = user
                    st.session_state['authenticated'] = True

                    # Clean up session
                    del st.session_state['awaiting_2fa']
                    del st.session_state['2fa_username']
                    del st.session_state['2fa_password']

                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Invalid verification code")

    if st.button("Cancel"):
        # Clean up session
        del st.session_state['awaiting_2fa']
        del st.session_state['2fa_username']
        del st.session_state['2fa_password']
        st.rerun()

def show_signup_page():
    st.title("📝 Sign Up")
    
    # Apply CSS for clear borders on text inputs
    st.markdown("""
    <style>
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput div[data-baseweb="input"] > div {
        border: 1px solid #ccc !important;
        border-radius: 4px !important;
        padding: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("signup_form"):
        st.subheader("Personal Information")
        first_name = st.text_input("First Name")
        surname = st.text_input("Surname")
        id_number = st.text_input("ID Number")
        
        st.subheader("Account Information")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        st.subheader("Department Information")
        # Department selection with improved UI
        department = st.selectbox(
            "Department",
            options=DEPARTMENTS,
            help="Select your department"
        )

        # Job title input/selection with better UX
        st.subheader("Job Position")
        existing_titles = get_job_titles()

        if existing_titles:
            job_title_option = st.radio(
                "Job Title Options",
                ["Select Existing Title", "Create New Title"],
                horizontal=True
            )

            if job_title_option == "Select Existing Title":
                job_title = st.selectbox(
                    "Select Job Title", 
                    options=existing_titles,
                    help="Choose from existing job titles in the organization"
                )
            else:
                job_title = st.text_input(
                    "Enter New Job Title",
                    help="Add a new job title to the organization"
                )
                st.info("This job title will be added to the database for future users")
        else:
            job_title = st.text_input(
                "Enter Job Title",
                help="You're creating the first job title in the system"
            )
            st.info("As the first user, your job title will be used as a template for future users")

        if st.form_submit_button("Create Account"):
            if not first_name or not surname or not id_number or not username or not email or not password or not department or not job_title:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    # Store first_name, surname, id_number in session state to pass to create_user
                    st.session_state['first_name'] = first_name
                    st.session_state['surname'] = surname 
                    st.session_state['id_number'] = id_number
                    user = create_user(username, email, password, department, job_title)
                    st.success("Account created successfully! Please login.")
                    st.session_state['show_login'] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating account: {str(e)}")

def show_auth_page():
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = True

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        show_login_page()

    with tab2:
        show_signup_page()