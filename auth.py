import streamlit as st
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


def init_auth_session():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def get_current_user() -> Optional[str]:
    return st.session_state.get("user")


def get_current_role() -> Optional[UserRole]:
    return st.session_state.get("user_role")


def has_access(required_role: UserRole) -> bool:
    current_role = get_current_role()
    if current_role is None:
        return False
    
    role_levels = {
        UserRole.USER: 1,
        UserRole.ADMIN: 2,
        UserRole.SUPERADMIN: 3
    }
    
    return role_levels.get(current_role, 0) >= role_levels.get(required_role, 0)


def login(username: str, password: str, role: str = UserRole.USER.value) -> bool:

    valid_users = {
        "john": {"password": "pass123", "role": UserRole.USER.value},
        "jane": {"password": "admin123", "role": UserRole.ADMIN.value},
        "root": {"password": "superadmin123", "role": UserRole.SUPERADMIN.value},
    }
    
    if username not in valid_users:
        return False
    
    user_data = valid_users[username]
    if user_data["password"] != password:
        return False
    
    st.session_state.user = username
    st.session_state.user_role = UserRole(user_data["role"])
    st.session_state.login_time = datetime.now()
    
    return True


def logout():
    st.session_state.user = None
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.rerun()


def require_auth(func):
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.error("Please login to access this page")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_role(required_role: UserRole):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_authenticated():
                st.error("Please login to access this page")
                st.stop()
            
            if not has_access(required_role):
                st.error(f"Access denied. This page requires {required_role.value.upper()} role.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
