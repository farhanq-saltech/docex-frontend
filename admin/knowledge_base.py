import streamlit as st
import httpx
import json

st.title("Knowledge Base")

if not st.session_state.get("username"):
    st.error("Please log in first")
    st.stop()

API_URL = "chatbot.saltechsystem.com:8000"

def get_knowledge_base_files():
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/api/admin/knowledge-base/files", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [f["file_name"] for f in data.get("files", [])]
            else:
                st.error(f"API error: {response.status_code}")
                return []
    except Exception as e:
        st.error(f"Could not connect to API: {str(e)}")
        return []


def get_kb_stats():
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/api/admin/knowledge-base/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        st.warning(f"Could not fetch KB stats: {str(e)}")
    return None


def upload_file_to_kb(file_data: bytes, filename: str) -> tuple:
    try:
        with httpx.Client(timeout=300) as client:
            files = {"file": (filename, file_data)}

            with client.stream("POST", f"{API_URL}/api/admin/knowledge-base/upload", files=files) as response:
                if response.status_code != 200:
                    return False, f"Upload failed: {response.status_code}"

                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            status = data.get("status")
                            message = data.get("message", "")

                            if status == "complete":
                                return True, message, data.get("vectors_added", 0)
                            elif status == "error":
                                return False, message, 0
                        except json.JSONDecodeError:
                            continue

                return False, "No response from server", 0

    except httpx.ConnectError:
        return False, "Cannot connect to API server", 0
    except Exception as e:
        return False, f"Upload error: {str(e)}", 0


st.markdown("### Knowledge Base Overview")

stats = get_kb_stats()
if stats and "total_vectors" in stats:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Files", stats.get("distinct_files", 0))
    with col2:
        st.metric("Total Vectors", stats.get("total_vectors", 0))
    with col3:
        st.metric("Collection Status", "✅ Ready" if stats.get("total_vectors", 0) > 0 else "⚠️ Empty")

st.divider()

st.markdown("### Add Files to Knowledge Base")
st.write("Supported formats: **PDF**, **DOCX**, **Images** (JPG, PNG, etc.), **Audio** (MP3, WAV, etc.), **Video** (MP4, AVI, etc.)")

uploaded_file = st.file_uploader(
    "Choose a file to add to the knowledge base",
    type=["pdf", "docx", "jpg", "jpeg", "png", "mp3", "wav", "mp4", "mkv"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

    st.write(f"📁 **File:** {uploaded_file.name}")
    st.write(f"📊 **Size:** {file_size_mb:.2f} MB")

    if file_size_mb > 500:
        st.error("❌ File is too large (maximum 500 MB)")
    else:
        if st.button("🚀 Upload and Process", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.info("📝 Initializing ingestion pipeline...")

            file_content = uploaded_file.getvalue()
            success, message, vectors_added = upload_file_to_kb(file_content, uploaded_file.name)

            if success:
                progress_bar.progress(100)
                st.success(f"✅ {message}\n\n**Vectors added:** {vectors_added}")
                st.balloons()

                st.session_state.uploaded_file = None
                st.rerun()
            else:
                progress_bar.progress(0)
                st.error(f"❌ {message}")

st.divider()

st.markdown("### Available Files in Knowledge Base")

files = get_knowledge_base_files()

if files:
    st.markdown(f"**Total files: {len(files)}**")

    cols = st.columns(2)
    for idx, file_name in enumerate(files):
        with cols[idx % 2]:
            st.write(f"📄 {file_name}")
else:
    st.info("No files in the knowledge base yet. Upload a file to get started!", icon="ℹ️")

st.divider()

if st.button("🔄 Refresh", use_container_width=True, key="refresh_kb"):
    st.rerun()
