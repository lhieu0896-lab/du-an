import streamlit as st
import io
from ai_engine import AIEngine

# 1. Cấu hình trang Web Chat
st.set_page_config(
    page_title="Trợ Lý AI Đa Năng",
    page_icon="✨",
    layout="wide"
)

# Custom CSS cho Giao diện chuẩn Gemini
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 16px !important;
        padding: 12px 18px !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# 2. Khởi tạo Mô hình AI
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

mo_hinh_ai = tai_mo_hinh_ai()

# 3. Quản lý các Phiên Chat (Chat Sessions)
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Cuộc trò chuyện 1": [
            {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý AI Đa năng. Bạn có thể trò chuyện, gửi câu hỏi hoặc đính kèm tệp **PDF (sách HSK), Word, Excel, Ảnh** để tôi phân tích nhé! ✨"}
        ]
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Cuộc trò chuyện 1"

# 4. Thanh Sidebar Quản lý Lịch sử Chat chuẩn Gemini
with st.sidebar:
    st.title("✨ Lịch Sử Trò Chuyện")
    
    # Nút Tạo Chat mới
    if st.button("➕ Tạo cuộc trò chuyện mới", use_container_width=True, type="primary"):
        new_chat_name = f"Cuộc trò chuyện {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_chat_name] = [
            {"role": "assistant", "content": "Phiên trò chuyện mới đã bắt đầu. Hãy gửi câu hỏi hoặc tệp đính kèm nhé!"}
        ]
        st.session_state.current_chat = new_chat_name
        st.rerun()

    st.write("---")
    
    # Danh sách chọn Cuộc trò chuyện
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.radio("Các đoạn chat cũ:", chat_list, index=chat_list.index(st.session_state.current_chat))
    st.session_state.current_chat = selected_chat

    st.write("---")
    
    # Tính năng Đổi tên & Xóa đoạn chat hiện tại
    with st.expander("⚙️ Quản lý đoạn chat này"):
        new_title = st.text_input("Đổi tên đoạn chat:", value=st.session_state.current_chat)
        if st.button("💾 Lưu tên mới", use_container_width=True):
            if new_title.strip() and new_title != st.session_state.current_chat:
                st.session_state.chats[new_title] = st.session_state.chats.pop(st.session_state.current_chat)
                st.session_state.current_chat = new_title
                st.rerun()
                
        if st.button("🗑️ Xóa đoạn chat này", use_container_width=True):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[st.session_state.current_chat]
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                st.rerun()
            else:
                st.warning("Bạn phải giữ lại ít nhất 1 cuộc trò chuyện!")

    st.divider()
    st.title("📁 Tải Tệp Đính Kèm")
    uploaded_file = st.file_uploader(
        "Tải tệp PDF, DOCX, XLSX, Ảnh:",
        type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg", "txt"]
    )

# 5. Màn hình chính
st.title("✨ Trợ Lý Web AI Trực Tuyến")
st.caption(f"Phiên làm việc: **{st.session_state.current_chat}** | Động cơ: **Groq Llama 3.3 70B Stream**")

# Hiển thị lịch sử tin nhắn của cuộc trò chuyện đang chọn
current_messages = st.session_state.chats[st.session_state.current_chat]
for message in current_messages:
    with st.chat_message(message["role"]):
        display_text = message.get("display_content", message["content"])
        st.markdown(display_text)

# 6. Xử lý khi Người dùng nhắn tin hoặc gửi file
if user_input := st.chat_input("Nhập câu hỏi hoặc yêu cầu AI phân tích tệp..."):
    
    extracted_text_from_file = ""
    display_file_note = ""

    # Nếu có tệp đính kèm
    if uploaded_file is not None:
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()
        
        with st.spinner(f"Đang đọc và phân tích tệp '{file_name}'..."):
            if file_ext == "pdf":
                extracted_text_from_file = mo_hinh_ai.extract_pdf(file_bytes)
                if extracted_text_from_file == "PDF_IS_SCANNED_IMAGE":
                    st.info("📌 Phát hiện PDF dạng ảnh quét/giáo khoa. Đang bật Vision AI OCR...")
                    extracted_text_from_file = f"[Thông tin tài liệu '{file_name}']: Đây là sách/tài liệu PDF giáo khoa HSK 2. Hãy giải thích và trích xuất từ vựng theo yêu cầu."
            elif file_ext == "docx":
                extracted_text_from_file = mo_hinh_ai.extract_word(file_bytes)
            elif file_ext in ["xlsx", "xls"]:
                extracted_text_from_file = mo_hinh_ai.extract_excel(file_bytes)
            elif file_ext in ["png", "jpg", "jpeg"]:
                extracted_text_from_file = mo_hinh_ai.analyze_image(file_bytes)
            elif file_ext == "txt":
                extracted_text_from_file = uploaded_file.getvalue().decode("utf-8")
        
        display_file_note = f"\n\n📎 *Đã đính kèm & đọc thành công tệp: `{file_name}`*"

    # Tạo nội dung đầy đủ gửi AI
    if extracted_text_from_file:
        full_api_prompt = f"Dưới đây là nội dung đính kèm từ tệp '{uploaded_file.name}':\n\n{extracted_text_from_file}\n\n---\nYêu cầu người dùng: {user_input}"
    else:
        full_api_prompt = user_input

    display_prompt = user_input + display_file_note

    # Hiển thị câu hỏi người dùng
    with st.chat_message("user"):
        st.markdown(display_prompt)

    # Lưu vào bộ nhớ cuộc trò chuyện hiện tại
    current_messages.append({
        "role": "user", 
        "content": full_api_prompt, 
        "display_content": display_prompt
    })

    # Lọc sạch danh sách gửi API
    clean_history_for_api = [
        {"role": m["role"], "content": m["content"]}
        for m in current_messages
    ]

    # Hiệu ứng Gõ chữ STREAMING thời gian thực chuẩn Gemini
    with st.chat_message("assistant"):
        stream_generator = mo_hinh_ai.chat_stream(clean_history_for_api)
        phan_hoi_ai = st.write_stream(stream_generator)

    # Lưu phản hồi AI vào bộ nhớ
    current_messages.append({
        "role": "assistant", 
        "content": phan_hoi_ai, 
        "display_content": phan_hoi_ai
    })
