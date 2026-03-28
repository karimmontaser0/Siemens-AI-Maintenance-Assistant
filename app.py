import streamlit as st
import os
from PIL import Image
from main import run_maintenance_assistant # بننادي المحرك بتاعنا

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Siemens AI Advisor", page_icon="🦾", layout="wide")

# --- الستايل (Sidebar) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Siemens-logo.svg", width=150)
    st.title("Settings")
    st.info("This AI agent uses RAG to analyze Siemens S7-1200 manuals and solve maintenance errors.")
    st.divider()
    st.write("🔧 **Engineer:** Kareem Montaser")

# --- الواجهة الرئيسية ---
st.title("🦾 AI Maintenance Advisor for Siemens PLC")
st.subheader("Your Intelligent Industrial Assistant")

# اختيار نوع المدخلات
tab1, tab2 = st.tabs(["💬 Ask a Question", "📸 Upload Error Image"])

with tab1:
    user_query = st.text_input("Describe the PLC issue or enter Error Code:", placeholder="e.g. How to fix error 80C4?")
    if st.button("Search Manual 🔍", key="text_btn"):
        if user_query:
            with st.spinner("Searching Siemens Manual..."):
                response = run_maintenance_assistant(user_query, is_image=False)
                st.markdown("### 🤖 AI Solution:")
                st.success(response)
        else:
            st.warning("Please enter a question first.")

with tab2:
    uploaded_file = st.file_uploader("Upload Diagnostic Buffer Screenshot (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        # عرض الصورة المرفوعة
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Diagnostic Buffer", use_container_width=True)
        
        if st.button("Analyze Image 📸", key="img_btn"):
            # حفظ الصورة مؤقتاً عشان دالة main تقرأها
            temp_path = "temp_upload.jpg"
            image.save(temp_path)
            
            with st.spinner("Analyzing Image & Searching Manual..."):
                response = run_maintenance_assistant(temp_path, is_image=True)
                st.markdown("### 🤖 AI Analysis & Solution:")
                st.success(response)
            
            # مسح الصورة المؤقتة بعد التشغيل
            if os.path.exists(temp_path):
                os.remove(temp_path)

# --- Footnote ---
st.divider()
st.caption("Developed by Mechatronics Engineer Kareem Montaser | Powered by Gemini 2.5 & LangChain")