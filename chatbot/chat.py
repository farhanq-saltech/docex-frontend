import streamlit as st
import requests
from datetime import datetime

st.title("💬 Chatbot")

API_URL = "http://chatbot.saltechsystems.com:8000"

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "sessions_loaded" not in st.session_state:
    st.session_state.sessions_loaded = False
if "message_sources" not in st.session_state:
    st.session_state.message_sources = {}

def load_user_sessions():
    if st.session_state.user_id:
        try:
            response = requests.get(
                f"{API_URL}/chat/sessions/{st.session_state.user_id}",
                timeout=10
            )
            if response.ok:
                st.session_state.chat_sessions = response.json()
                st.session_state.sessions_loaded = True
        except Exception as e:
            st.warning(f"Could not load chat history: {str(e)}")

def load_session_messages(session_id: str):
    try:
        response = requests.get(
            f"{API_URL}/chat/sessions/{session_id}/messages",
            timeout=10
        )
        if response.ok:
            messages = response.json()
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            st.session_state.session_id = session_id
    except Exception as e:
        st.error(f"Could not load session: {str(e)}")

def delete_session(session_id: str):
    try:
        response = requests.delete(
            f"{API_URL}/chat/sessions/{session_id}",
            timeout=10
        )
        if response.ok:
            st.session_state.messages = []
            st.session_state.session_id = None
            load_user_sessions()
            st.rerun()
        else:
            st.error("Could not delete session")
    except Exception as e:
        st.error(f"Error deleting session: {str(e)}")

def create_new_session():
    st.session_state.session_id = None
    st.session_state.messages = []

def create_session_on_first_message():
    try:
        session_response = requests.post(
            f"{API_URL}/chat/sessions/",
            json={"user_id": st.session_state.user_id},
            timeout=5
        )
        if session_response.ok:
            new_session_id = session_response.json().get("session_id")
            st.session_state.session_id = new_session_id
            load_user_sessions()
            return new_session_id
    except Exception as e:
        st.error(f"Could not create session: {str(e)}")
        return None

def deduplicate_sources(sources):
    """Remove duplicate sources, keeping the highest score for each file"""
    seen = {}
    for source in sources:
        file_name = source.get('file_name', 'Unknown')
        score = source.get('score', 0)
        
        if file_name not in seen or score > seen[file_name]['score']:
            seen[file_name] = source
    
    return list(seen.values())

if not st.session_state.user_id:
    try:
        user_response = requests.post(
            f"{API_URL}/chat/users/",
            json={"username": st.session_state.username},
            timeout=5
        )
        if user_response.ok:
            user_data = user_response.json()
            st.session_state.user_id = user_data.get("id")
            load_user_sessions()
            if st.session_state.chat_sessions and not st.session_state.session_id:
                load_session_messages(st.session_state.chat_sessions[0]["session_id"])
    except Exception as e:
        st.warning(f"Could not initialize user: {str(e)}")
else:
    if not st.session_state.sessions_loaded:
        load_user_sessions()
        if st.session_state.chat_sessions and not st.session_state.session_id:
            load_session_messages(st.session_state.chat_sessions[0]["session_id"])

with st.sidebar:
    st.divider()
    
    st.markdown("### Chat Management")
    if st.button("➕ New Chat", use_container_width=True):
        create_new_session()
    
    st.markdown("### Conversations")
    
    if st.session_state.chat_sessions:
        for session in st.session_state.chat_sessions:
            if st.button(
                session["title"],
                key=f"session_{session['session_id']}",
                use_container_width=True,
                help=session["title"]
            ):
                load_session_messages(session["session_id"])
    else:
        st.info("No conversations yet. Start a new chat!", icon="ℹ️")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        
        # Display sources if they exist for this message
        if message["role"] == "assistant" and i in st.session_state.message_sources:
            sources = st.session_state.message_sources[i]
            if sources:
                sources = deduplicate_sources(sources)
                with st.expander("📚 View Sources"):
                    for source in sources:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(f"📄 {source.get('file_name', 'Unknown')}")
                        with col2:
                            score = source.get('score', 0)
                            st.metric("Match", f"{score:.1%}")

if prompt := st.chat_input("Ask a question about your documents..."):
    if not st.session_state.session_id:
        session_id = create_session_on_first_message()
        if not session_id:
            st.error("Could not create chat session")
            st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat/",
                    json={
                        "session_id": st.session_state.session_id,
                        "message": prompt
                    },
                    timeout=60
                )
                
                if response.ok:
                    data = response.json()
                    ai_response = data.get("response", "No response received")
                    sources = data.get("sources", [])
                    
                    st.markdown(ai_response, unsafe_allow_html=True)
                    
                    # Display sources expandable section (deduplicated)
                    if sources:
                        sources = deduplicate_sources(sources)
                        with st.expander("📚 View Sources"):
                            for source in sources:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.text(f"📄 {source.get('file_name', 'Unknown')}")
                                with col2:
                                    score = source.get('score', 0)
                                    st.metric("Match", f"{score:.1%}")
                else:
                    ai_response = f"Error: {response.status_code} - {response.text}"
                    sources = []
                    st.error(ai_response)
            except requests.exceptions.ConnectionError:
                ai_response = f"Could not connect to API at {API_URL}. Is it running?"
                sources = []
                st.error(ai_response)
            except Exception as e:
                ai_response = f"Error: {str(e)}"
                sources = []
                st.error(ai_response)
    
    if 'ai_response' in locals():
        message_index = len(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        if sources:
            sources = deduplicate_sources(sources)
            st.session_state.message_sources[message_index] = sources
        load_user_sessions()
