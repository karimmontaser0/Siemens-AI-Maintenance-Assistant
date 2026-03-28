import streamlit as st
import os
from main import run_maintenance_assistant

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Siemens AI Advisor",
    page_icon="🦾",
    layout="wide"
)

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.title("SIEMENS")
    st.markdown("---")
    st.info("This AI agent uses **RAG** to analyze Siemens S7-1200 manuals and solve maintenance errors.")
    st.markdown("---")
    st.write("👨‍💻 **Engineer:** Kareem Montaser")

# --- 3. MAIN UI COMPONENTS ---
st.title("🦾 AI Maintenance Advisor for Siemens PLC")
st.subheader("Your Intelligent Industrial Assistant")

# Tabs for different input methods
tab1, tab2 = st.tabs(["💬 Ask a Question", "📸 Upload Error Image"])

# --- TAB 1: TEXT QUERY ---
with tab1:
    user_query = st.text_input("Describe the PLC issue or enter Error Code:", 
                                placeholder="e.g. What is the default IP address?")
    search_button = st.button("Search Manual 🔍")

    if search_button and user_query:
        with st.spinner("Analyzing manual..."):
            response = run_maintenance_assistant(user_query, is_image=False)
            st.markdown("### 🤖 AI Solution:")
            st.success(response)

# --- TAB 2: IMAGE ANALYSIS ---
with tab2:
    uploaded_file = st.file_uploader("Upload TIA Portal Screenshot", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        # Save temp file for processing
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)
        
        if st.button("Analyze Image 🔎"):
            with st.spinner("Processing image and searching manual..."):
                response = run_maintenance_assistant(temp_path, is_image=True)
                st.markdown("### 🤖 AI Solution:")
                st.success(response)
                
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --- 4. FOOTER ---
st.markdown("---")
st.caption("Developed by Mechatronics Engineer Kareem Montaser | Powered by Gemini & LangChain")