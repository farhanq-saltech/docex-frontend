import io
import requests
import streamlit as st

API_DEFAULT = "http://10.102.10.9:8000/api"


def api_post_upload(api_base: str, file_bytes: bytes, filename: str):
    files = {"file": (filename, file_bytes, "application/pdf")}
    return requests.post(f"{api_base}/upload", files=files)


def api_get_files(api_base: str):
    return requests.get(f"{api_base}/files")


def api_get_file(api_base: str, file_id: int):
    return requests.get(f"{api_base}/files/{file_id}")


def api_download_file(api_base: str, file_id: int):
    return requests.get(f"{api_base}/files/{file_id}/download")


def api_generate_notes(api_base: str, file_id: int):
    return requests.post(f"{api_base}/files/{file_id}/notes/generate")


def api_extract_file(api_base: str, file_id: int):
    return requests.post(f"{api_base}/files/{file_id}/extract")


def api_update_file(api_base: str, file_id: int, data: dict):
    return requests.put(f"{api_base}/files/{file_id}", json=data)


def api_list_notes(api_base: str, file_id: int):
    return requests.get(f"{api_base}/files/{file_id}/notes")


def api_get_note(api_base: str, note_id: int):
    return requests.get(f"{api_base}/notes/{note_id}")


def api_update_note(api_base: str, note_id: int, data: dict):
    return requests.put(f"{api_base}/notes/{note_id}", json=data)


def api_delete_note(api_base: str, note_id: int):
    return requests.delete(f"{api_base}/notes/{note_id}")


def api_generate_pdf(api_base: str, file_id: int):
    return requests.get(f"{api_base}/files/{file_id}/generate-pdf")


def main():
    if not st.session_state.get("username"):
        st.error("Please log in first")
        st.stop()

    st.set_page_config(page_title="10Fold Admin", layout="wide")

    st.title("10Fold — Meeting Notes")

    api_base = st.sidebar.text_input("API base URL (include /api)", value=API_DEFAULT)

    st.sidebar.header("History")
    try:
        files_resp = api_get_files(api_base)
        files_list = files_resp.json() if files_resp.ok else []
    except Exception:
        files_list = []

    for f in files_list:
        if st.sidebar.button(f.get("original_filename") or f.get("filename"), key=f"hist_{f.get('id')}"):
            st.session_state["selected_file"] = f.get("id")

    main_tabs = st.tabs(["Upload", "Results"])

    with main_tabs[0]:
        st.header("Upload PDF")
        uploaded = st.file_uploader("Choose a PDF", type=["pdf"]) 
        
        if uploaded is not None:
            file_bytes = uploaded.read()
            st.pdf(file_bytes)
            
            if st.button("Extract Text", type="primary"):
                with st.spinner("Extracting text..."):
                    try:
                        resp = api_post_upload(api_base, file_bytes, uploaded.name)
                        if resp.ok:
                            file_id = resp.json().get("id")
                            st.session_state["temp_file_id"] = file_id
                            
                            eresp = api_extract_file(api_base, file_id)
                            if eresp.ok:
                                st.success("Text extracted successfully")
                                st.rerun()
                            else:
                                st.error(f"Extraction failed: {eresp.status_code} {eresp.text}")
                        else:
                            st.error(f"File processing failed: {resp.status_code} {resp.text}")
                    except Exception as e:
                        st.error(str(e))
            
            temp_id = st.session_state.get("temp_file_id")
            if temp_id:
                try:
                    fresp = api_get_file(api_base, temp_id)
                    if fresp.ok:
                        fobj = fresp.json()
                        extracted = fobj.get("extracted_text") or ""
                        
                        if extracted:
                            st.markdown("### Extracted Text")
                            txt = st.text_area("Edit text below:", value=extracted, height=400, key="edit_text")
                            
                            if st.button("Save Edits and Extract Summary and Tasks", type="primary"):
                                with st.spinner("Saving and generating..."):
                                    try:
                                        u = api_update_file(api_base, temp_id, {"extracted_text": txt, "status": "completed"})
                                        if u.ok:
                                            gen = api_generate_notes(api_base, temp_id)
                                            if gen.ok:
                                                st.success("Saved and generated summary & tasks!")
                                                st.session_state["selected_file"] = temp_id
                                                st.session_state["temp_file_id"] = None
                                                st.rerun()
                                            else:
                                                st.warning(f"Saved but generation failed: {gen.status_code}")
                                        else:
                                            st.error(f"Save failed: {u.status_code} {u.text}")
                                    except Exception as e:
                                        st.error(str(e))
                            
                            if st.button("Add meeting to vector knowledge base"):
                                st.info("Coming soon!")
                except Exception as e:
                    st.error(str(e))

    with main_tabs[1]:
        st.header("Results")
        sel = st.session_state.get("selected_file")
        
        if not sel:
            st.info("Process a file first to view results.")
        else:
            try:
                resp = api_get_file(api_base, sel)
                if resp.ok:
                    file_obj = resp.json()
                    st.subheader(file_obj.get("original_filename"))
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Project", file_obj.get("project_name") or "—")
                    col2.metric("Date", file_obj.get("meeting_date") or "—")
                    
                    if file_obj.get("participants"):
                        st.info(f"**Participants:** {file_obj.get('participants')}")
                    
                    if file_obj.get("extracted_text"):
                        st.markdown("### Extracted Text")
                        st.text_area("Extracted content:", value=file_obj.get("extracted_text"), height=250, disabled=True)
                    
                    st.markdown("---")
                    st.markdown("### Notes")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    notes = []
                    notes_resp = api_list_notes(api_base, sel)
                    if notes_resp.ok:
                        notes = notes_resp.json()
                    
                    with col2:
                        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
                            with st.spinner("Generating PDF..."):
                                try:
                                    pdf_resp = api_generate_pdf(api_base, sel)
                                    if pdf_resp.ok:
                                        st.download_button(
                                            label="Download PDF",
                                            data=pdf_resp.content,
                                            file_name=f"meeting_minutes_{sel}.pdf",
                                            mime="application/pdf"
                                        )
                                        st.success("PDF generated!")
                                    else:
                                        st.error(f"PDF generation failed: {pdf_resp.status_code}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    with col1:
                        if not notes:
                            st.info("No notes yet. Generate them from the Upload tab.")
                        else:
                            for n in notes:
                                with st.expander(f"{n.get('note_type').upper()} (Status: {n.get('status')})"):
                                    content = st.text_area("content", height=200, value=n.get("content") or "")
                                    col1a, col2a = st.columns(2)
                                    if col1a.button("Save", key=f"s_{n.get('id')}"):
                                        try:
                                            u = api_update_note(api_base, n.get("id"), {"content": content})
                                            if u.ok:
                                                st.success("Saved")
                                                st.rerun()
                                            else:
                                                st.error(f"Save failed: {u.status_code}")
                                        except Exception as e:
                                            st.error(str(e))
                                    if col2a.button("Delete", key=f"d_{n.get('id')}"):
                                        try:
                                            d = api_delete_note(api_base, n.get("id"))
                                            if d.ok:
                                                st.success("Deleted")
                                                st.rerun()
                                            else:
                                                st.error(f"Delete failed: {d.status_code}")
                                        except Exception as e:
                                            st.error(str(e))
                else:
                    st.error(f"Error fetching file: {resp.status_code}")
            except Exception as e:
                st.error(str(e))


if __name__ == "__main__":
    main()
