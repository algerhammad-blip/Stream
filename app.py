import streamlit as st
import os
import shutil
import time

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="SwiftDrop Cloud", page_icon="🚀", layout="wide")

# Force Light Theme (Light Blue & White)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: #f0f7ff !important;
    }
    
    /* Force Dark Text for everything */
    h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
        color: #0d1b2a !important;
    }

    /* Professional Blue Headers */
    .main-title {
        color: #1a7fe0 !important;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0;
    }

    /* Fix Blackish boxes on Mobile */
    div[data-testid="stExpander"], .stChatMessage, .stLoading {
        background-color: #ffffff !important;
        border: 1px solid #c8ddf0 !important;
    }

    /* Buttons: Solid Blue with White Text */
    .stButton>button {
        background-color: #1a7fe0 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        width: 100%;
    }

    /* Download Buttons */
    .stDownloadButton>button {
        background-color: #00b96b !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        width: 100%;
    }

    /* File Uploader Box */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #1a7fe0 !important;
        border-radius: 15px;
    }

    /* Custom File Card */
    .file-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #1a7fe0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STORAGE LOGIC ---
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path): os.makedirs(path)
    return path

# --- 3. MAIN APP ---
def main():
    st.markdown('<p class="main-title">🚀 SwiftDrop Cloud</p>', unsafe_allow_html=True)
    st.markdown("<p style='color:#4a6080;'>Professional Cross-Device Transfer</p>", unsafe_allow_html=True)

    if 'room_id' not in st.session_state:
        st.session_state.room_id = ""

    # Room Connection Area
    with st.container():
        st.write("---")
        col1, col2 = st.columns([3, 1])
        room_input = col1.text_input("Enter 4-Digit Room Code", value=st.session_state.room_id, placeholder="e.g. 1234")
        if col2.button("Connect"):
            st.session_state.room_id = room_input
            st.rerun()

    if not st.session_state.room_id:
        st.info("👋 Use the same Room Code on both devices to start sharing.")
        return

    room_dir = get_room_dir(st.session_state.room_id)
    st.success(f"✅ Linked to Room: {st.session_state.room_id}")

    tab1, tab2 = st.tabs(["📤 Upload Files", "📥 Available Files"])

    # --- UPLOAD TAB ---
    with tab1:
        st.write("### Select Files to Send")
        uploaded_files = st.file_uploader("", accept_multiple_files=True)
        
        if st.button("⚡ Start Fast Upload"):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(room_dir, uploaded_file.name)
                    
                    # UI Components
                    status = st.empty()
                    p_bar = st.progress(0)
                    m1, m2, m3 = st.columns(3)
                    
                    # File Processing with Visual Progress
                    with open(file_path, "wb") as f:
                        total_size = uploaded_file.size
                        chunk_size = max(total_size // 20, 1024 * 100) # Dynamic chunks
                        bytes_written = 0
                        t0 = time.time()
                        
                        # We use getbuffer() then chunk it for the progress effect
                        content = uploaded_file.getbuffer()
                        
                        while bytes_written < total_size:
                            chunk = content[bytes_written : bytes_written + chunk_size]
                            f.write(chunk)
                            bytes_written += len(chunk)
                            
                            # Update UI
                            elapsed = time.time() - t0
                            speed = (bytes_written / (elapsed if elapsed > 0 else 0.01))
                            eta = (total_size - bytes_written) / (speed if speed > 0 else 1)
                            
                            p_bar.progress(bytes_written / total_size)
                            status.text(f"Processing: {uploaded_file.name}")
                            m1.metric("Speed", f"{speed/1024/1024:.1f} MB/s")
                            m2.metric("Done", f"{int(bytes_written/total_size*100)}%")
                            m3.metric("ETA", f"{int(eta)}s")
                            
                            # Small artificial sleep to prevent UI crash & allow user to see bar
                            time.sleep(0.05)
                            
                    st.toast(f"Finished: {uploaded_file.name}")
                st.success("All files uploaded successfully!")
                time.sleep(1)
                st.rerun()

    # --- DOWNLOAD TAB ---
    with tab2:
        st.write("### Files in this Room")
        if st.button("🔄 Refresh List"):
            st.rerun()

        files = os.listdir(room_dir)
        if not files:
            st.info("No files here yet.")
        else:
            for file_name in files:
                file_path = os.path.join(room_dir, file_name)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                # Professional Card UI
                st.markdown(f"""
                    <div class="file-card">
                        <strong>📄 {file_name}</strong><br>
                        <small>Size: {size_mb:.2f} MB</small>
                    </div>
                """, unsafe_allow_html=True)
                
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {file_name}",
                        data=f,
                        file_name=file_name,
                        key=file_name
                    )

    # --- SIDEBAR SETTINGS ---
    with st.sidebar:
        st.title("⚙️ Settings")
        if st.button("🗑️ Reset Room"):
            if os.path.exists(room_dir):
                shutil.rmtree(room_dir)
            st.success("Room cleared.")
            st.rerun()
        
        st.write("---")
        st.caption("SwiftDrop Cloud v2.0 - Professional Edition")

if __name__ == "__main__":
    main()
