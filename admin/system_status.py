import streamlit as st
import httpx
from datetime import datetime

st.title("🔧 System Status")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

API_URL = "chatbot.saltechsystems.com:8000"

def get_system_status():
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/api/admin/system/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        st.error(f"Could not reach API: {str(e)}")
        return None

def test_service(service_name):
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/api/admin/system/health/{service_name}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("connected", False)
            return False
    except:
        return False

system_status = get_system_status()

if system_status:
    api_online = system_status["api"]["status"]
    ollama_online = system_status["ollama"]["status"]
    qdrant_online = system_status["qdrant"]["status"]
else:
    api_online = ollama_online = qdrant_online = False

st.markdown("### Service Status")

col1, col2, col3 = st.columns(3)
with col1:
    status = "🟢 Online" if api_online else "🔴 Offline"
    st.metric("FastAPI Backend", status)
with col2:
    status = "🟢 Online" if ollama_online else "🔴 Offline"
    st.metric("Ollama LLM", status)
with col3:
    status = "🟢 Online" if qdrant_online else "🔴 Offline"
    st.metric("Qdrant Vector DB", status)

st.divider()

st.markdown("### System Metrics")
col1, col2 = st.columns(2)

with col1:
    if api_online:
        try:
            with httpx.Client() as client:
                response = client.get(f"{API_URL}/api/admin/knowledge-base/stats", timeout=5)
                if response.ok:
                    stats = response.json()
                    file_count = stats.get("distinct_files", 0)
                    vector_count = stats.get("total_vectors", 0)
                    st.metric("Knowledge Base Files", file_count)
                    st.metric("Total Vectors", vector_count)
                else:
                    st.metric("Knowledge Base Files", "—")
        except:
            st.metric("Knowledge Base Files", "Error")
    else:
        st.metric("Knowledge Base Files", "API Offline")

    st.metric("Active Sessions", "—")

with col2:
    st.metric("Chat Messages", "—")
    st.metric("Total Users", 3)

st.divider()

st.markdown("### Connection Tests")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔌 FastAPI", use_container_width=True, key="test_api"):
        if test_service("api"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

with col2:
    if st.button("🔌 Ollama", use_container_width=True, key="test_ollama"):
        if test_service("ollama"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

with col3:
    if st.button("🔌 Qdrant", use_container_width=True, key="test_qdrant"):
        if test_service("qdrant"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

st.divider()

with st.expander("⚙️ Configuration"):
    st.markdown("### Service URLs")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("FastAPI URL", value=API_URL, disabled=True)
        st.text_input("Ollama URL", value="http://localhost:11434", disabled=True)
    with col2:
        st.text_input("Qdrant Path", value="qd_db/", disabled=True)

    st.markdown("---")
    if st.button("🔄 Refresh Status", type="primary", use_container_width=True):
        st.rerun()

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
