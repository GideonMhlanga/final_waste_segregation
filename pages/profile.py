
import streamlit as st
import qrcode
import io
import base64
from auth.auth_handler import update_user, generate_2fa_qrcode, verify_2fa_setup, disable_2fa, DEPARTMENTS
from models.database import User, get_session

def show_profile_page():
    if not st.session_state.get('authenticated') or not st.session_state.get('user'):
        st.error("You must be logged in to view this page.")
        return
    
    st.title("👤 User Profile")
    
    user = st.session_state['user']
    
    tabs = st.tabs(["Profile Information", "Security Settings"])
    
    with tabs[0]:
        show_profile_information(user)
    
    with tabs[1]:
        show_security_settings(user)

def show_profile_information(user):
    st.header("Profile Information")
    
    with st.form("edit_profile_form"):
        st.text_input("Username", value=user.username, disabled=True, 
                     help="Username cannot be changed")
        
        email = st.text_input("Email", value=user.email)
        
        department = st.selectbox(
            "Department",
            options=DEPARTMENTS,
            index=DEPARTMENTS.index(user.department) if user.department in DEPARTMENTS else 0
        )
        
        job_title = st.text_input("Job Title", value=user.job_title)
        
        if st.form_submit_button("Update Profile"):
            success, message = update_user(
                user.id,
                email=email,
                department=department,
                job_title=job_title
            )
            
            if success:
                st.success(message)
                # Update session user
                session = get_session()
                updated_user = session.query(User).get(user.id)
                st.session_state['user'] = updated_user
                st.rerun()
            else:
                st.error(message)
    
    st.divider()
    
    # Account information
    st.subheader("Account Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.write("**Account Created:**")
        st.write("**Department:**")
        st.write("**Job Title:**")
        st.write("**Two-Factor Auth:**")
    
    with info_col2:
        st.write(user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        st.write(user.department)
        st.write(user.job_title)
        st.write("Enabled" if user.two_factor_enabled else "Disabled")

def show_security_settings(user):
    st.header("Security Settings")
    
    # Two-Factor Authentication
    st.subheader("Two-Factor Authentication (2FA)")
    
    if user.two_factor_enabled:
        st.success("Two-factor authentication is enabled for your account.")
        
        if st.button("Disable Two-Factor Authentication"):
            success, message = disable_2fa(user.id)
            if success:
                st.success(message)
                # Update session user
                session = get_session()
                updated_user = session.query(User).get(user.id)
                st.session_state['user'] = updated_user
                st.rerun()
            else:
                st.error(message)
    else:
        st.warning("Two-factor authentication is not enabled for your account.")
        
        if 'setup_2fa' not in st.session_state:
            if st.button("Set Up Two-Factor Authentication"):
                st.session_state['setup_2fa'] = True
                st.rerun()
        else:
            # Step 1: Show QR code
            st.write("**Step 1:** Scan this QR code with your authenticator app (e.g., Google Authenticator, Authy)")
            
            qr_code, secret_key = generate_2fa_qrcode(user.id)
            
            if qr_code:
                st.image(f"data:image/png;base64,{qr_code}", width=200)
                st.code(secret_key, language=None)
                st.info("If you can't scan the QR code, you can manually enter the secret key above into your authenticator app.")
                
                # Step 2: Verify code
                st.write("**Step 2:** Enter the verification code from your authenticator app")
                
                verification_code = st.text_input("Verification Code", max_chars=6)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Verify and Enable 2FA"):
                        if not verification_code:
                            st.error("Please enter the verification code")
                        else:
                            success, message = verify_2fa_setup(user.id, verification_code)
                            if success:
                                st.success(message)
                                # Update session user
                                session = get_session()
                                updated_user = session.query(User).get(user.id)
                                st.session_state['user'] = updated_user
                                del st.session_state['setup_2fa']
                                st.rerun()
                            else:
                                st.error(message)
                
                with col2:
                    if st.button("Cancel Setup"):
                        del st.session_state['setup_2fa']
                        st.rerun()
            else:
                st.error("Failed to generate QR code. Please try again later.")
                if st.button("Cancel"):
                    del st.session_state['setup_2fa']
                    st.rerun()
    
    # Change Password
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            else:
                from auth.auth_handler import check_password, hash_password
                
                # Verify current password
                if check_password(user.password, current_password):
                    # Update password
                    session = get_session()
                    user_obj = session.query(User).get(user.id)
                    user_obj.password = hash_password(new_password)
                    session.commit()
                    st.success("Password changed successfully")
                else:
                    st.error("Current password is incorrect")

if __name__ == "__main__":
    show_profile_page()
