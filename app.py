import streamlit as st
import os
import shutil
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="SwiftDrop Cloud", page_icon="🚀", layout="wide")

# Directory to store shared files
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- THEME LOCK CSS (Fixes Mobile Visibility) ---
st.markdown("""
    <style>
    /* Force Light Mode Colors for Visibility */
    .stApp {
        background-color: #f0f7ff !important;
    }
    
    /* Force all text to be Dark Blue/Black */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #0d1b2a !important;
    }

    /* Make the Room Card very visible */
    .room-info {
        background-color: #ffffff !important;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #1a7fe0 !important;
        margin-bottom: 20px;
        color: #0d1b2a !important;
    }

    /* Professional File Card */
    .file-card {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #c8ddf0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        margin-bottom: 15px;
    }

    /* Style Buttons to be solid and bright */
    .stButton>button {
        background-color: #1a7fe0 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
    }

    /* Style the File Uploader box */
    section[data-testid="stFileUploadDropzone"] {
        background-color: white !important;
        border: 2px dashed #1a7fe0 !important;
    }

    /* Fix Tab text visibility */
    button[data-baseweb="tab"] p {
        color: #1a7fe0 !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---

def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def main():
    st.title("🚀 SwiftDrop Cloud")
    st.markdown("### Professional Cross-Device File Sharing")

    # Room ID logic
    if 'room_id' not in st.session_state:
        st.session_state.room_id = ""

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### Connect")
        room_input = st.text_input("Enter 4-Digit Room Code", value=st.session_state.room_id, help="Use the same code on both devices")
        if st.button("Join Room"):
            st.session_state.room_id = room_input
            st.rerun()

    if not st.session_state.room_id:
        st.info("Enter a Room Code to start sharing. Try '1234'.")
        return

    # Connected State
    room_dir = get_room_dir(st.session_state.room_id)
    
    st.markdown(f"""
        <div class="room-info">
            <strong>📍 Room Code: {st.session_state.room_id}</strong><br>
            <span style="color: #00b96b;">● Connected & Ready</span>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📤 Send to Cloud", "📥 Get Files"])

    with tab1:
        st.write("### Upload")
        uploaded_files = st.file_uploader("Upload files from this device", accept_multiple_files=True)
        
        if st.button("⚡ Upload Now"):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(room_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"Successfully uploaded {len(uploaded_files)} files!")
                time.sleep(1)
                st.rerun()

    with tab2:
        st.write("### Available in Room")
        files = os.listdir(room_dir)
        
        if st.button("🔄 Refresh List"):
            st.rerun()

        if not files:
            st.write("No files shared yet.")
        else:
            for file_name in files:
                file_path = os.path.join(room_dir, file_name)
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                
                # Using a container for the file card
                with st.container():
                    st.markdown(f"""
                    <div class='file-card'>
                        <span style='font-size: 20px;'>📄</span> <strong>{file_name}</strong><br>
                        <span style='color: #4a6080;'>Size: {file_size:.2f} MB</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"Download {file_name}",
                            data=f,
                            file_name=file_name,
                            key=f"dl_{file_name}"
                        )

    # Sidebar for Reset
    with st.sidebar:
        st.write("### Settings")
        if st.button("🗑️ Clear This Room"):
            if os.path.exists(room_dir):
                shutil.rmtree(room_dir)
                os.makedirs(room_dir)
            st.success("Room cleared.")
            st.rerun()
        
        st.write("---")
        st.write("SwiftDrop Cloud v1.0")

if __name__ == "__main__":
    main()
