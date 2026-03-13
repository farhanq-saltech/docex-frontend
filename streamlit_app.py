import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

USERS = {
    "john": {"password": "pass123", "role": "User"},
    "jane": {"password": "admin123", "role": "Admin"},
    "root": {"password": "superadmin123", "role": "Superadmin"},
}


def login():
    st.header("Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username", placeholder="john, jane, or root")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]
                st.session_state.user_id = None
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.chat_sessions = []
                st.success(f"Welcome {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown("---")
        st.markdown("### Demo Credentials")
        st.markdown("""
        **User Account:**
        - Username: `john`
        - Password: `pass123`
        
        **Admin Account:**
        - Username: `jane`
        - Password: `admin123`
        
        **Superadmin Account:**
        - Username: `root`
        - Password: `superadmin123`
        """)


def logout():
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Logout", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

chat_page = st.Page(
    "chatbot/chat.py",
    title="Chatbot",
    icon=":material/chat:",
    default=(role == "User"),
)

pdf_processor = st.Page(
    "summarizer/pdf_processor.py",
    title="Meeting Summarizer",
    icon=":material/description:",
    default=(role == "Admin"),
)

user_management = st.Page(
    "admin/user_management.py",
    title="User Management",
    icon=":material/person_add:",
    default=(role == "Superadmin"),
)
system_status = st.Page(
    "admin/system_status.py",
    title="System Status",
    icon=":material/settings:",
)
knowledge_base = st.Page(
    "admin/knowledge_base.py",
    title="Knowledge Base",
    icon=":material/library_books:",
)

account_pages = [settings, logout_page]

page_dict = {}

if role in ["User", "Admin", "Superadmin"]:
    page_dict["Main"] = [chat_page]

if role in ["Admin", "Superadmin"]:
    page_dict["Meeting"] = [pdf_processor]

if role == "Superadmin":
    page_dict["Admin"] = [user_management, system_status, knowledge_base]

if role in ["User", "Admin", "Superadmin"]:
    page_dict["Account"] = account_pages

st.set_page_config(page_title="10Fold", page_icon="📚", layout="wide")

if role:
    st.title("📚 10Fold")

if len(page_dict) > 0:
    pg = st.navigation(page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
