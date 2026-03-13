import streamlit as st

st.title("👥 User Management")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("#### Users")
with col2:
    if st.button("➕ Add User"):
        st.session_state.show_add_user = True

users = [
    {"id": 1, "username": "john", "role": "USER", "status": "Active"},
    {"id": 2, "username": "jane", "role": "ADMIN", "status": "Active"},
    {"id": 3, "username": "root", "role": "SUPERADMIN", "status": "Active"},
]

for user in users:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{user['username']}**")
        with col2:
            st.badge(user['role'])
        with col3:
            st.caption(user['status'])
        with col4:
            if user['role'] != 'SUPERADMIN':
                col4a, col4b = st.columns(2)
                with col4a:
                    st.button("✎", key=f"edit_{user['id']}")
                with col4b:
                    st.button("✕", key=f"delete_{user['id']}")

st.divider()

with st.expander("➕ Add New User"):
    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("Username")
        new_role = st.selectbox("Role", ["USER", "ADMIN"])
    with col2:
        new_password = st.text_input("Password", type="password")
        st.text_input("Confirm Password", type="password")
    
    if st.button("Create User", type="primary", use_container_width=True):
        if new_username and new_password:
            st.success(f"User '{new_username}' created")
        else:
            st.error("Fill all fields")
