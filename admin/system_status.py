import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

st.title("🔧 System Status")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

API_URL = "http://10.102.10.9:8000"
OLLAMA_URL = "http://localhost:11434"
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

def test_connection(url, name):
    try:
        if "ollama" in name.lower():
            response = requests.get(f"{url}/api/tags", timeout=3)
        elif "qdrant" in name.lower():
            response = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, verify=False)
            if response.collection_exists("pdf_knowledge_base"):
                return True
        else:
            response = requests.get(f"{url}/health", timeout=3)
        
        return response.status_code == 200
    except:
        return False

api_online = test_connection(API_URL, "API")
ollama_online = test_connection(OLLAMA_URL, "Ollama")
qdrant_online = test_connection(QDRANT_URL, "Qdrant")

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
            response = requests.get(f"{API_URL}/api/files", timeout=5)
            if response.ok:
                file_count = len(response.json())
                st.metric("Total PDFs", file_count)
            else:
                st.metric("Total PDFs", "—")
        except:
            st.metric("Total PDFs", "Error")
    else:
        st.metric("Total PDFs", "API Offline")
    
    st.metric("Active Sessions", "—")

with col2:
    st.metric("Chat Messages", "—")
    st.metric("Total Users", 3)

st.divider()

st.markdown("### Connection Tests")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔌 FastAPI", use_container_width=True, key="test_api"):
        if test_connection(API_URL, "API"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

with col2:
    if st.button("🔌 Ollama", use_container_width=True, key="test_ollama"):
        if test_connection(OLLAMA_URL, "Ollama"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

with col3:
    if st.button("🔌 Qdrant", use_container_width=True, key="test_qdrant"):
        if test_connection(QDRANT_URL, "Qdrant"):
            st.success("✓ Connected")
        else:
            st.error("✗ Offline")

st.divider()

with st.expander("⚙️ Configuration"):
    st.markdown("### Service URLs")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("FastAPI URL", value=API_URL, disabled=True)
        st.text_input("Ollama URL", value=OLLAMA_URL, disabled=True)
    with col2:
        st.text_input("Qdrant URL", value=QDRANT_URL, disabled=True)
    
    st.markdown("---")
    if st.button("🔄 Refresh Status", type="primary", use_container_width=True):
        st.rerun()

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
