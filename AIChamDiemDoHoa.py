import streamlit as st
import docx
import pypdf
import google.generativeai as genai

st.set_page_config(page_title="AI Grader - HUTECH", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stTextInput input, .stTextArea textarea { background-color: #010409 !important; color: #3fb950 !important; border: 1px solid #30363d !important; font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 MODULE AI CHẤM ĐIỂM BÁO CÁO")
st.subheader("Đồ Án Xe 2 Bánh Cân Bằng")

with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    api_key = st.text_input("Nhập Gemini API Key của bạn:", type="password")
    
    st.markdown("---")
    st.markdown("**Barem chấm điểm (Tối đa 9.0đ):**")
    st.markdown("- CLO3 (1.5đ): Phân tích & Giải pháp")
    st.markdown("- CLO3 (1.5đ): Kiến trúc & Thuật toán")
    st.markdown("- CLO1 (2.0đ): Giao diện HMI")
    st.markdown("- CLO2 (2.0đ): Triển khai & Tích hợp")
    st.markdown("- CLO2,3 (1.5đ): Kiểm thử & Phân tích")
    st.markdown("- CLO3 (0.5đ): Chất lượng tài liệu")

uploaded_file = st.file_uploader("Tải lên báo cáo (.docx hoặc .pdf)", type=['docx', 'pdf'])

def extract_text(file, file_name):
    full_text = []
    if file_name.endswith('.docx'):
        doc = docx.Document(file)
        full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    elif file_name.endswith('.pdf'):
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text: full_text.append(text.strip())
    return ' \n'.join(full_text)

if st.button("🚀 BẮT ĐẦU CHẤM ĐIỂM", use_container_width=True):
    if not api_key or not uploaded_file:
        st.warning("⚠️ Vui lòng nhập API Key và tải file lên!")
    else:
        with st.spinner("AI đang phân tích và đối chiếu Rubric..."):
            text = extract_text(uploaded_file, uploaded_file.name)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash')
            prompt = f"""
            Đóng vai Giảng viên chấm đồ án 'Xe 2 bánh cân bằng'. Chấm điểm dựa trên Rubric sau:
            1. Phân tích yêu cầu & Giải pháp (CLO3 - Tối đa 1.5đ)
            2. Kiến trúc & Thuật toán (CLO3 - Tối đa 1.5đ)
            3. Giao diện HMI (CLO1 - Tối đa 2.0đ)
            4. Triển khai & Tích hợp (CLO2 - Tối đa 2.0đ)
            5. Kiểm thử & Phân tích (CLO2, CLO3 - Tối đa 1.5đ)
            6. Chất lượng tài liệu (CLO3 - Tối đa 0.5đ)
            Format trả về: [TÊN TIÊU CHÍ]: [Điểm/Tối đa] - [Nhận xét ngắn gọn]
            >> TỔNG ĐIỂM BÁO CÁO: [Tổng]/9.0
            NỘI DUNG BÁO CÁO: {text}
            """
            response = model.generate_content(prompt)
            st.success("✅ HOÀN TẤT CHẤM ĐIỂM")
            st.text_area("KẾT QUẢ ĐÁNH GIÁ", value=response.text, height=450)