import streamlit as st
import os
import shutil
import time
import qrcode
from io import BytesIO

# --- 1. TOFFEE-STYLE UI ---
st.set_page_config(page_title="ToffeeDrop Cloud", page_icon="🍬", layout="centered")

st.markdown("""
    <style>
    /* Professional Clean Look */
    .stApp { background-color: #ffffff !important; }
    
    /* Center everything */
    .block-container { padding-top: 2rem !important; }

    /* Blue Highlight Theme */
    h1, h2, h3 { color: #1a7fe0 !important; font-family: 'Inter', sans-serif; text-align: center; }
    
    /* Status Box */
    .status-card {
        background: #f0f7ff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #c8ddf0;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Force Light Mode for Mobile */
    input, label, .stMarkdown { color: #0d1b2a !important; }
    
    /* Large Mobile-Friendly Buttons */
    .stButton>button {
        background-color: #1a7fe0 !important;
        color: white !important;
        border-radius: 50px !important;
        height: 3.5em !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div { background-color: #1a7fe0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FAST STORAGE ---
BASE_DIR = "/tmp/toffeedrop"
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

def main():
    st.write("### 🍬 ToffeeDrop")
    st.caption("P2P-Inspired Cloud Transfer")

    if 'room' not in st.session_state: st.session_state.room = ""

    # --- STEP 1: PAIRING (The Toffeeshare way) ---
    if not st.session_state.room:
        st.markdown('<div class="status-card">Select a Room Code to pair devices</div>', unsafe_allow_html=True)
        room_code = st.text_input("Enter 4-Digit Code", placeholder="e.g. 9999")
        if st.button("Create / Join Room"):
            st.session_state.room = room_code
            st.rerun()
        return

    room_path = os.path.join(BASE_DIR, st.session_state.room)
    if not os.path.exists(room_path): os.makedirs(room_path)

    # --- STEP 2: QR CODE GENERATOR ---
    # This lets you scan your PC screen with your phone to join instantly
    with st.expander("📱 Scan to Join on Mobile"):
        url = f"https://scrapper1000.streamlit.app/?room={st.session_state.room}" # Update with your real URL
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, caption="Scan this with your phone camera")

    st.success(f"📍 Room: {st.session_state.room}")

    # --- STEP 3: THE BRIDGE (Transfer) ---
    tab_send, tab_receive = st.tabs(["🚀 SEND", "📥 RECEIVE"])

    with tab_send:
        # We use st.file_uploader but write to disk immediately
        files = st.file_uploader("Drop files here", accept_multiple_files=True)
        if files:
            if st.button("START TRANSFER"):
                bar = st.progress(0)
                for i, f in enumerate(files):
                    with open(os.path.join(room_path, f.name), "wb") as out:
                        out.write(f.getbuffer())
                    bar.progress((i + 1) / len(files))
                st.toast("Files sent!")
                time.sleep(0.5)
                st.rerun()

    with tab_receive:
        room_files = os.listdir(room_path)
        if st.button("🔄 Refresh"): st.rerun()

        if not room_files:
            st.info("Waiting for sender...")
        else:
            for fn in room_files:
                f_path = os.path.join(room_path, fn)
                f_size = os.path.getsize(f_path) / (1024*1024)
                
                # We use the most direct download trigger
                with open(f_path, "rb") as f_data:
                    st.download_button(
                        label=f"⬇️ Download {fn} ({f_size:.1f}MB)",
                        data=f_data,
                        file_name=fn,
                        key=fn,
                        use_container_width=True
                    )

    # --- FOOTER SETTINGS ---
    st.write("---")
    if st.button("🚪 Leave & Clear Room"):
        if os.path.exists(room_path): shutil.rmtree(room_path)
        st.session_state.room = ""
        st.rerun()

if __name__ == "__main__":
    main()
