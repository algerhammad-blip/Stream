import streamlit as st
import os
import shutil
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="SwiftDrop Cloud", page_icon="🚀", layout="wide")

# Directory to store shared files on the server
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .stApp { background-color: #f0f7ff; }
    .file-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddeeff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .status-online { color: #00b96b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---

def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def main():
    # --- HEADER ---
    st.title("🚀 SwiftDrop Cloud")
    st.caption("Professional Cross-Device File Sharing")

    # --- ROOM JOINING ---
    if 'room_id' not in st.session_state:
        st.session_state.room_id = ""

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Connect")
        room_input = st.text_input("Enter Room Code (e.g., 1234)", value=st.session_state.room_id)
        if st.button("Join Room"):
            st.session_state.room_id = room_input
            st.rerun()

    if not st.session_state.room_id:
        st.info("Enter a Room Code to start sharing. Use the same code on both devices.")
        return

    # --- ROOM INTERFACE ---
    room_dir = get_room_dir(st.session_state.room_id)
    
    st.divider()
    st.markdown(f"Connected to Room: **{st.session_state.room_id}** <span class='status-online'>● Live</span>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📤 Send Files", "📥 Available Files"])

    with tab1:
        st.subheader("Upload to Room")
        uploaded_files = st.file_uploader("Choose files to share", accept_multiple_files=True)
        
        if st.button("⚡ Upload to Cloud"):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(room_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded {len(uploaded_files)} files! Tell the other device to refresh.")
                time.sleep(1)
                st.rerun()

    with tab2:
        st.subheader("Files from Other Devices")
        files = os.listdir(room_dir)
        
        if st.button("🔄 Refresh List"):
            st.rerun()

        if not files:
            st.info("No files in this room yet.")
        else:
            for file_name in files:
                file_path = os.path.join(room_dir, file_name)
                file_size = os.path.getsize(file_path) / (1024 * 1024) # MB
                
                # Professional File Card UI
                with st.container():
                    st.markdown(f"""
                    <div class='file-card'>
                        <strong>📄 {file_name}</strong><br>
                        <small>Size: {file_size:.2f} MB</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download {file_name}",
                            data=f,
                            file_name=file_name,
                            key=file_name
                        )

    # --- SIDEBAR / FOOTER ---
    with st.sidebar:
        st.header("Storage Management")
        if st.button("🗑️ Clear Room Files"):
            shutil.rmtree(room_dir)
            os.makedirs(room_dir)
            st.success("Room cleared.")
            st.rerun()
        
        st.divider()
        st.write("Files are automatically cleared when the Streamlit server restarts.")

if __name__ == "__main__":
    main()