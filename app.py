import streamlit as st
import os
import shutil
import time

# --- CONFIG ---
st.set_page_config(page_title="SwiftDrop Pro", page_icon="🚀", layout="wide")

# Directory setup
BASE_DIR = "/tmp/swiftdrop_rooms"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- AGGRESSIVE LIGHT-THEME CSS ---
st.markdown("""
    <style>
    /* Force high-contrast colors for every element */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f0f7ff !important;
        color: #0d1b2a !important;
    }
    
    /* Fix buttons and inputs that turn black on mobile */
    .stButton>button, .stDownloadButton>button {
        background-color: #1a7fe0 !important;
        color: white !important;
        border: none !important;
        opacity: 1 !important;
    }
    
    input, [data-testid="stFileUploadDropzone"] {
        background-color: white !important;
        color: black !important;
        border: 2px solid #1a7fe0 !important;
    }

    div[data-baseweb="tab-list"] {
        background-color: white !important;
        border-radius: 10px;
    }

    /* Professional Metrics Styling */
    .metric-box {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #c8ddf0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def get_room_dir(room_id):
    path = os.path.join(BASE_DIR, room_id)
    if not os.path.exists(path): os.makedirs(path)
    return path

def main():
    st.title("🚀 SwiftDrop Cloud")
    
    if 'room_id' not in st.session_state: st.session_state.room_id = ""

    # Room Connection
    with st.expander("🔑 Connection Settings", expanded=not st.session_state.room_id):
        room_input = st.text_input("Enter Room Code", value=st.session_state.room_id)
        if st.button("Connect"):
            st.session_state.room_id = room_input
            st.rerun()

    if not st.session_state.room_id:
        st.warning("Please connect to a room first.")
        return

    room_dir = get_room_dir(st.session_state.room_id)
    st.success(f"Connected to Room: {st.session_state.room_id}")

    tab1, tab2 = st.tabs(["📤 Send Files", "📥 Available Files"])

    with tab1:
        st.subheader("Upload to Cloud")
        uploaded_files = st.file_uploader("Select files", accept_multiple_files=True)
        
        if st.button("⚡ Start Transfer") and uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(room_dir, uploaded_file.name)
                total_size = uploaded_file.size
                
                # Setup UI for Progress
                status_text = st.empty()
                progress_bar = st.progress(0)
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with open(file_path, "wb") as f:
                    start_time = time.time()
                    bytes_written = 0
                    chunk_size = 1024 * 500 # 500KB chunks for smoother bars
                    
                    # Simulation loop to show progress as we write to server disk
                    while bytes_written < total_size:
                        chunk = uploaded_file.read(chunk_size)
                        if not chunk: break
                        f.write(chunk)
                        bytes_written += len(chunk)
                        
                        # Calculations
                        elapsed_time = time.time() - start_time
                        speed = bytes_written / (elapsed_time if elapsed_time > 0 else 0.1) # bytes/sec
                        progress = bytes_written / total_size
                        eta = (total_size - bytes_written) / speed if speed > 0 else 0
                        
                        # Update UI
                        status_text.text(f"Transferring: {uploaded_file.name}")
                        progress_bar.progress(progress)
                        metric_col1.metric("Speed", f"{speed/1024/1024:.2f} MB/s")
                        metric_col2.metric("Progress", f"{int(progress*100)}%")
                        metric_col3.metric("ETA", f"{int(eta)}s")
                        
                st.success(f"✓ {uploaded_file.name} Uploaded")
            time.sleep(1)
            st.rerun()

    with tab2:
    st.subheader("📥 Available in Room")
    if st.button("🔄 Refresh List"): 
        st.rerun()
    
    files = os.listdir(room_dir)
    if not files:
        st.info("No files in this room.")
    else:
        for file_name in files:
            file_path = os.path.join(room_dir, file_name)
            sz_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Create a professional card for each file
            with st.container():
                col_a, col_b = st.columns([3, 1])
                col_a.markdown(f"📄 **{file_name}**  \n*{sz_mb:.2f} MB*")
                
                # UNIQUE KEY for each file to prevent Streamlit errors
                prep_key = f"prep_{file_name}"
                
                # Step 1: User clicks to "Prepare" the data
                if prep_key not in st.session_state:
                    if col_b.button("Prepare ⬇️", key=f"btn_{file_name}"):
                        with st.spinner("Preparing..."):
                            # Read file into memory
                            with open(file_path, "rb") as f:
                                st.session_state[prep_key] = f.read()
                        st.rerun()
                
                # Step 2: Once prepared, show the actual Download button
                else:
                    col_b.download_button(
                        label="Save ✅",
                        data=st.session_state[prep_key],
                        file_name=file_name,
                        mime="application/octet-stream",
                        key=f"dl_{file_name}"
                    )
                    # Option to clear memory after preparing
                    if st.button("Reset 🔄", key=f"reset_{file_name}"):
                        del st.session_state[prep_key]
                        st.rerun()
            st.divider()

    with st.sidebar:
        st.header("Storage")
        if st.button("🗑️ Clear Room"):
            shutil.rmtree(room_dir)
            st.rerun()

if __name__ == "__main__":
    main()
