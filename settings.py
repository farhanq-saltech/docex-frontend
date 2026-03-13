import streamlit as st

st.title("⚙️ Settings")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

st.markdown("### API Configuration")

col1, col2 = st.columns(2)
with col1:
    api_url = st.text_input("Unified API URL", "http://10.102.10.9:8000")
    ollama_url = st.text_input("Ollama URL", "http://10.102.10.9:11434")
with col2:
    qdrant_url = st.text_input("Qdrant URL", "http://10.102.10.9:6333")
    api_key = st.text_input("Qdrant API Key (from .env)", type="password")

st.divider()

st.markdown("### Preferences")

theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
language = st.selectbox("Language", ["English", "Spanish", "French"])

st.divider()

if st.button("💾 Save Settings", type="primary", use_container_width=True):
    st.success("Settings saved successfully")

if st.button("🔄 Reset to Defaults", use_container_width=True):
    st.info("Settings reset to defaults")
