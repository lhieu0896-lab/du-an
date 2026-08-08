import streamlit as st
import io
from ai_engine import AIEngine

# 1. Cấu hình trang Web Chat
st.set_page_config(
    page_title="Trợ Lý Web AI Đa Năng",
    page_icon="🤖",
    layout="wide"
)

# 2. Khởi tạo Mô hình AI
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

mo_hinh_ai = tai_mo_hinh_ai()

# 3. Khởi tạo Lịch sử Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý AI Đa năng. Bạn có thể trò chuyện hoặc đính kèm tệp **PDF, Word, Excel, Ảnh (PNG, JPG)** để tôi phân tích giúp nhé!"}
    ]

# 4. Thanh Sidebar Tải Tệp & Tùy chọn
with st.sidebar:
    st.title("📁 Tải Tệp Tài Liệu / Ảnh")
    st.caption("Hỗ trợ tệp: PDF, DOCX, XLSX, XLS, PNG, JPG, JPEG, TXT")
    
    uploaded_file = st.file_uploader(
        "Chọn tệp đính kèm gửi cho AI:",
        type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg", "txt"]
    )
    
    st.divider()
    st.title("⚙️ Tùy Chọn")
    st.write("🤖 **Model Văn bản:** Groq Llama 3.3 70B")
    st.write("👁️ **Model Hình ảnh:** Groq Llama 3.2 Vision 11B")
    
    if st.button("🗑️ Xóa Lịch Sử Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Lịch sử trò chuyện đã được làm mới. Hãy gửi câu hỏi hoặc tệp mới nhé!"}
        ]
        st.rerun()

# 5. Tiêu đề ứng dụng
st.title("💬 Trợ Lý AI Đa Năng & Đa Phương Tiện")
st.caption("Hệ thống Web AI thuần túy - Phân tích tệp Văn bản, Bảng tính Excel & Nhận diện Hình ảnh")

# 6. Hiển thị Lịch sử Tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Xử lý khi Người dùng gửi câu hỏi hoặc tải tệp
if user_input := st.chat_input("Nhập câu hỏi hoặc yêu cầu AI phân tích..."):
    
    # 7a. Nếu có tệp đính kèm từ Sidebar
    file_content_prompt = ""
    if uploaded_file is not None:
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()
        
        with st.spinner(f"Đang xử lý tệp {file_name}..."):
            try:
                if file_ext == "pdf":
                    text_extracted = mo_hinh_ai.extract_pdf(file_bytes)
                    file_content_prompt = f"\n\n[Nội dung từ tệp PDF '{file_name}']:\n{text_extracted}"
                elif file_ext == "docx":
                    text_extracted = mo_hinh_ai.extract_word(file_bytes)
                    file_content_prompt = f"\n\n[Nội dung từ tệp Word '{file_name}']:\n{text_extracted}"
                elif file_ext in ["xlsx", "xls"]:
                    text_extracted = mo_hinh_ai.extract_excel(file_bytes)
                    file_content_prompt = f"\n\n[Dữ liệu Bảng tính Excel '{file_name}']:\n{text_extracted}"
                elif file_ext in ["png", "jpg", "jpeg"]:
                    text_extracted = mo_hinh_ai.analyze_image(file_bytes)
                    file_content_prompt = f"\n\n[Kết quả phân tích từ Hình Ảnh '{file_name}']:\n{text_extracted}"
                elif file_ext == "txt":
                    text_extracted = uploaded_file.getvalue().decode("utf-8")
                    file_content_prompt = f"\n\n[Nội dung tệp TXT '{file_name}']:\n{text_extracted}"
            except Exception as err:
                st.error(f"Lỗi đọc tệp {file_name}: {err}")

    # Gộp tin nhắn người dùng nhập + nội dung tệp (nếu có)
    full_user_content = user_input + file_content_prompt
    display_content = user_input
    if uploaded_file:
        display_content += f"\n\n📎 *Đã đính kèm tệp: `{uploaded_file.name}`*"

    # Hiển thị tin nhắn người dùng lên màn hình chat
    with st.chat_message("user"):
        st.markdown(display_content)
    
    # Lưu vào bộ nhớ Session
    st.session_state.messages.append({"role": "user", "content": full_user_content})

    # Gọi AI trả lời
    with st.chat_message("assistant"):
        with st.spinner("AI đang phân tích và soạn câu trả lời..."):
            history_for_api = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            phan_hoi_ai = mo_hinh_ai.chat_with_memory(history_for_api)
            st.markdown(phan_hoi_ai)

    # Lưu câu trả lời AI vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": phan_hoi_ai})
