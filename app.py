import streamlit as st
import os
import shutil
import time

# --- 1. PROFESSIONAL THEME (Light Blue & White) ---
st.set_page_config(page_title="SwiftDrop Cloud", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    /* Main Background */
    .stApp { background: #f8fbff !important; }
    
    /* Global Text Colors */
    h1, h2, h3, p, label, .stMarkdown { color: #1e293b !important; }

    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #1a7fe0, #5ba8f0);
        padding: 20px;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(26,127,224,0.2);
    }
    
    /* Solid Professional Buttons */
    .stButton>button {
        background-color: #1a7fe0 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        height: 3em !important;
        width: 100%;
    }

    /* File Cards */
    .file-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Fix for Mobile Dark Mode */
    input, .stTextInput>div>div>input {
        background-color: white !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DIRECTORY LOGIC ---
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path): os.makedirs(path)
    return path

# --- 3. MAIN INTERFACE ---
def main():
    st.markdown('<div class="main-header"><h1>🚀 SwiftDrop Cloud</h1><p>Professional Secure File Transfer</p></div>', unsafe_allow_html=True)

    # Initialize Session States
    if 'room_id' not in st.session_state: st.session_state.room_id = ""
    if 'prepared_file' not in st.session_state: st.session_state.prepared_file = None

    # Room Connection
    col1, col2 = st.columns([3, 1])
    room_input = col1.text_input("Room Code", value=st.session_state.room_id, placeholder="Enter 4 digits (e.g. 8888)")
    if col2.button("Connect"):
        st.session_state.room_id = room_input
        st.rerun()

    if not st.session_state.room_id:
        st.info("💡 Enter a Room Code to pair devices. No account needed.")
        return

    room_dir = get_room_dir(st.session_state.room_id)
    st.success(f"Linked to Room: {st.session_state.room_id}")

    tab_send, tab_get = st.tabs(["📤 Send Files", "📥 Receive Files"])

    # --- UPLOAD SECTION ---
    with tab_send:
        st.write("### 1. Select Files")
        uploaded_files = st.file_uploader("Upload will start automatically after selecting", accept_multiple_files=True)
        
        if uploaded_files:
            st.write("### 2. Finalize Transfer")
            if st.button("🚀 Push to Room"):
                with st.status("Transferring to Cloud...", expanded=True) as status:
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(room_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            shutil.copyfileobj(uploaded_file, f)
                        st.write(f"✅ {uploaded_file.name} saved.")
                    status.update(label="Transfer Complete!", state="complete", expanded=False)
                st.toast("Files are now available in the room!")
                time.sleep(1)
                st.rerun()

    # --- DOWNLOAD SECTION ---
    with tab_get:
        st.write("### Files in Room")
        files = os.listdir(room_dir)
        
        if st.button("🔄 Refresh List"):
            st.rerun()

        if not files:
            st.write("No files shared yet.")
        else:
            for file_name in files:
                file_path = os.path.join(room_dir, file_name)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                # Card Layout
                with st.container():
                    col_file, col_btn = st.columns([3, 1])
                    col_file.markdown(f"📄 **{file_name}**  \n`{size_mb:.2f} MB`")
                    
                    # Logic to prevent multiple popups
                    prep_id = f"prep_{file_name}"
                    if st.session_state.prepared_file != file_name:
                        if col_btn.button("Prepare ⬇️", key=f"btn_{file_name}"):
                            with st.spinner("Processing..."):
                                # Load into memory
                                with open(file_path, "rb") as f:
                                    st.session_state[prep_id] = f.read()
                                st.session_state.prepared_file = file_name
                            st.rerun()
                    else:
                        # Show the actual download button only when ready
                        col_btn.download_button(
                            label="Save ✅",
                            data=st.session_state[prep_id],
                            file_name=file_name,
                            key=f"dl_{file_name}"
                        )
                        if st.button("Cancel", key=f"can_{file_name}"):
                            st.session_state.prepared_file = None
                            st.rerun()
                st.divider()

    # --- SIDEBAR ---
    with st.sidebar:
        st.write("### ⚙️ Room Settings")
        if st.button("🗑️ Clear Room"):
            if os.path.exists(room_dir):
                shutil.rmtree(room_dir)
            st.session_state.room_id = ""
            st.rerun()
        st.write("---")
        st.caption("SwiftDrop Cloud v3.0 | Intern Project")

if __name__ == "__main__":
    main()
