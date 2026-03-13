import streamlit as st
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

st.title("Knowledge Base")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def get_knowledge_base_files():
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, verify=False)
        collection_name = "pdf_knowledge_base"
        file_names = []
        
        offset = None
        while True:
            scroll_result, next_page_offset = client.scroll(
                collection_name=collection_name,
                scroll_filter=None,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            for point in scroll_result:
                if point.payload and "file_name" in point.payload:
                    file_names.append(point.payload["file_name"])
            
            if next_page_offset is None:
                break
            offset = next_page_offset
        
        return sorted(list(set(file_names)))
    except Exception as e:
        st.error(f"Could not connect to knowledge base: {str(e)}")
        return []

st.markdown("### Available Files in Knowledge Base")

files = get_knowledge_base_files()

if files:
    st.markdown(f"**Total files: {len(files)}**")
    for file_name in files:
        st.markdown(f"- {file_name}")
else:
    st.info("No files in the knowledge base yet.", icon="ℹ️")

st.divider()

if st.button("Add additional files to the knowledge base", use_container_width=True):
    st.info("Coming soon!")
