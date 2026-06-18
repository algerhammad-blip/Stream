import streamlit as st
import os
import shutil
import time

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="SwiftDrop Cloud Pro", page_icon="🚀", layout="wide")

# Directory setup on Streamlit Server
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- AGGRESSIVE CSS FOR MOBILE VISIBILITY & THEME LOCK ---
st.markdown("""
    <style>
    /* Force Light Mode - Background & Text */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f0f7ff !important;
        color: #0d1b2a !important;
    }
    
    /* Force Sidebar Visibility */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #c8ddf0;
    }

    /* Professional Metric Styling */
    [data-testid="stMetricValue"] {
        color: #1a7fe0 !important;
        font-weight: bold !important;
    }

    /* Button Styling - Fixes Blackish appearance on Mobile Dark Mode */
    .stButton>button {
        background-color: #1a7fe0 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    
    /* Input Boxes */
    input {
        background-color: #ffffff !important;
        color: #0d1b2a !important;
        border: 2px solid #1a7fe0 !important;
    }

    /* File Uploader visibility */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #1a7fe0 !important;
        color: #0d1b2a !important;
    }

    /* Tab Label Visibility */
    button[data-baseweb="tab"] p {
        color: #1a7fe0 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* File Card Styling */
    .file-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #c8ddf0;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(26,127,224,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path): os.makedirs(path)
    return path

def format_size(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def main():
    st.title("🚀 SwiftDrop Cloud")
    st.markdown("##### High-Speed Professional File Transfer")

    # Session State for Room ID
    if 'room_id' not in st.session_state:
        st.session_state.room_id = ""

    # --- CONNECTION SECTION ---
    with st.expander("🔑 Connection & Room Settings", expanded=not st.session_state.room_id):
        col1, col2 = st.columns([2, 1])
        room_input = col1.text_input("Enter Room Code (e.g., 5555)", value=st.session_state.room_id)
        if col2.button("Connect Room"):
            st.session_state.room_id = room_input
            st.rerun()

    if not st.session_state.room_id:
        st.warning("Please enter a Room Code to connect devices.")
        return

    room_dir = get_room_dir(st.session_state.room_id)
    st.success(f"Connected to Room: {st.session_state.room_id} | Status: Online")

    # --- TABS ---
    tab1, tab2 = st.tabs(["📤 Upload Files", "📥 Available Files"])

    # --- TAB 1: UPLOAD WITH PROGRESS, SPEED & ETA ---
    with tab1:
        st.subheader("Send to Room")
        uploaded_files = st.file_uploader("Select files from this device", accept_multiple_files=True)
        
        if st.button("⚡ Start Transfer") and uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(room_dir, uploaded_file.name)
                total_size = uploaded_file.size
                
                # UI Placeholders
                status_text = st.empty()
                progress_bar = st.progress(0)
                m1, m2, m3 = st.columns(3)
                
                with open(file_path, "wb") as f:
                    start_time = time.time()
                    bytes_written = 0
                    chunk_size = 1024 * 1024 # 1MB chunks
                    
                    while bytes_written < total_size:
                        chunk = uploaded_file.read(chunk_size)
                        if not chunk: break
                        f.write(chunk)
                        bytes_written += len(chunk)
                        
                        # Calculate Metrics
                        elapsed = time.time() - start_time
                        speed = bytes_written / (elapsed if elapsed > 0 else 0.01)
                        progress = bytes_written / total_size
                        eta = (total_size - bytes_written) / speed if speed > 0 else 0
                        
                        # Update UI
                        status_text.text(f"Uploading: {uploaded_file.name}")
                        progress_bar.progress(progress)
                        m1.metric("Speed", f"{speed/1024/1024:.2f} MB/s")
                        m2.metric("Progress", f"{int(progress*100)}%")
                        m3.metric("ETA", f"{int(eta)}s")

                st.success(f"✓ {uploaded_file.name} successfully shared.")
            time.sleep(1)
            st.rerun()

    # --- TAB 2: DOWNLOAD WITH PREPARE LOGIC ---
    with tab2:
        st.subheader("Files in this Room")
        if st.button("🔄 Refresh List"): st.rerun()
        
        files = os.listdir(room_dir)
        if not files:
            st.info("Room is currently empty.")
        else:
            for file_name in files:
                file_path = os.path.join(room_dir, file_name)
                sz = os.path.getsize(file_path)
                
                # Dynamic UI Card
                st.markdown(f"""
                <div class="file-card">
                    <strong>📄 {file_name}</strong><br>
                    <small>Size: {format_size(sz)}</small>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                
                # PREPARE vs DOWNLOAD Logic
                prep_key = f"data_{file_name}"
                if prep_key not in st.session_state:
                    if c1.button("Prepare ⬇️", key=f"p_{file_name}"):
                        with st.spinner("Processing..."):
                            with open(file_path, "rb") as f:
                                st.session_state[prep_key] = f.read()
                        st.rerun()
                else:
                    c1.download_button("Save ✅", data=st.session_state[prep_key], file_name=file_name, key=f"dl_{file_name}")
                    if c2.button("Clear Cache", key=f"clr_{file_name}"):
                        del st.session_state[prep_key]
                        st.rerun()
                st.write("---")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Room Management")
        if st.button("🗑️ Clear All Room Files"):
            shutil.rmtree(room_dir)
            st.session_state.room_id = ""
            st.rerun()
        
        st.divider()
        st.markdown("### Intern Project: SwiftDrop Cloud")
        st.caption("Secure Local-Server File Sharing")

if __name__ == "__main__":
    main()
