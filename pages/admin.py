import streamlit as st
import pandas as pd
from auth.auth_handler import get_all_users, create_user, delete_user, DEPARTMENTS
from models.database import User, get_session

def show_admin_panel():
    st.title("👑 Admin Panel")
    
    if not st.session_state.get('authenticated') or not st.session_state.get('user') or not st.session_state.get('user').job_title.lower() in ['admin', 'administrator', 'manager']:
        st.error("You don't have permission to access this page.")
        return
    
    tabs = st.tabs(["User Management", "System Settings"])
    
    with tabs[0]:
        show_user_management()
    
    with tabs[1]:
        show_system_settings()

def show_user_management():
    st.header("User Management")
    
    # Get all users
    users = get_all_users()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Users")
        if users:
            users_data = [{
                "ID": user.id,
                "Username": user.username,
                "Email": user.email,
                "Department": user.department,
                "Job Title": user.job_title,
                "Created": user.created_at.strftime("%Y-%m-%d")
            } for user in users]
            
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
            
            # User actions
            selected_user = st.selectbox("Select User for Action", 
                                         options=[f"{user.username} ({user.email})" for user in users])
            
            username = selected_user.split(" (")[0] if selected_user else None
            
            if username:
                col_edit, col_delete, col_reset = st.columns(3)
                
                with col_edit:
                    if st.button("Edit User", use_container_width=True):
                        st.session_state['user_to_edit'] = username
                
                with col_delete:
                    if st.button("Delete User", use_container_width=True):
                        try:
                            delete_user(username)
                            st.success(f"User {username} deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete user: {str(e)}")
                
                with col_reset:
                    if st.button("Reset Password", use_container_width=True):
                        st.session_state['user_to_reset_password'] = username
        else:
            st.info("No users found in the system.")
    
    with col2:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_department = st.selectbox("Department", options=DEPARTMENTS)
            new_job_title = st.text_input("Job Title")
            
            if st.form_submit_button("Add User"):
                if not new_username or not new_email or not new_password or not new_department or not new_job_title:
                    st.error("Please fill in all fields")
                else:
                    try:
                        create_user(new_username, new_email, new_password, new_department, new_job_title)
                        st.success(f"User {new_username} created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create user: {str(e)}")
    
    # Edit user details if selected
    if st.session_state.get('user_to_edit'):
        st.subheader(f"Edit User: {st.session_state['user_to_edit']}")
        
        session = get_session()
        user = session.query(User).filter_by(username=st.session_state['user_to_edit']).first()
        
        if user:
            with st.form("edit_user_form"):
                edit_email = st.text_input("Email", value=user.email)
                edit_department = st.selectbox("Department", options=DEPARTMENTS, index=DEPARTMENTS.index(user.department) if user.department in DEPARTMENTS else 0)
                edit_job_title = st.text_input("Job Title", value=user.job_title)
                
                if st.form_submit_button("Save Changes"):
                    try:
                        user.email = edit_email
                        user.department = edit_department
                        user.job_title = edit_job_title
                        session.commit()
                        st.success("User updated successfully!")
                        del st.session_state['user_to_edit']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update user: {str(e)}")
            
            if st.button("Cancel"):
                del st.session_state['user_to_edit']
                st.rerun()
    
    # Reset password if selected
    if st.session_state.get('user_to_reset_password'):
        st.subheader(f"Reset Password: {st.session_state['user_to_reset_password']}")
        
        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Reset Password"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_password:
                    st.error("Password cannot be empty")
                else:
                    from auth.reset_password import reset_user_password
                    success, message = reset_user_password(st.session_state['user_to_reset_password'], new_password)
                    if success:
                        st.success(message)
                        del st.session_state['user_to_reset_password']
                        st.rerun()
                    else:
                        st.error(message)
        
        if st.button("Cancel Reset"):
            del st.session_state['user_to_reset_password']
            st.rerun()

def show_system_settings():
    st.header("System Settings")
    st.info("System settings will be implemented in future updates.")

if __name__ == "__main__":
    show_admin_panel()