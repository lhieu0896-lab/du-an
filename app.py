import streamlit as st
import io
import uuid
from ai_engine import AIEngine

# 1. Cấu hình trang
st.set_page_config(
    page_title="Trợ Lý Web AI Vĩnh Viễn Pro",
    page_icon="✨",
    layout="wide"
)

# 2. Khởi tạo Engine
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

mo_hinh_ai = tai_mo_hinh_ai()
db_status = getattr(mo_hinh_ai, "db_status", "CHƯA_KẾT_NỐI")

# 3. Đồng bộ Lịch sử từ Database
if "chats" not in st.session_state or not st.session_state.chats:
    db_chats = mo_hinh_ai.load_all_chats() if hasattr(mo_hinh_ai, "load_all_chats") else {}
    if db_chats:
        st.session_state.chats = db_chats
        st.session_state.current_chat = list(db_chats.keys())[0]
    else:
        init_id = str(uuid.uuid4())
        default_title = "Cuộc trò chuyện mới"
        init_msg = "Xin chào! Lịch sử chat được lưu vĩnh viễn trên Database. Hệ thống đã tích hợp **Tìm kiếm Web Real-time**, **Tự động đặt tên Chat** và **Phân tích Tài liệu Dài (RAG)**! ✨"
        st.session_state.chats = {
            default_title: {
                "id": init_id,
                "messages": [
                    {"role": "assistant", "content": init_msg, "display_content": init_msg}
                ]
            }
        }
        st.session_state.current_chat = default_title
        if db_status == "ĐÃ_KẾT_NỐI" and hasattr(mo_hinh_ai, "save_chat_node"):
            mo_hinh_ai.save_chat_node(init_id, default_title)
            mo_hinh_ai.save_message(init_id, "assistant", init_msg, init_msg)

# 4. Thanh Sidebar Quản lý Lịch sử Chat Vĩnh Viễn
with st.sidebar:
    st.title("✨ Lịch Sử Trò Chuyện (DB)")
    
    if db_status == "ĐÃ_KẾT_NỐI":
        st.success("🟢 Đã kết nối Supabase (Lưu vĩnh viễn)")
    else:
        st.error(f"🔴 Chưa lưu DB: {db_status}")
    
    st.write("---")
    
    # Nút bật/tắt Tìm kiếm Web Real-time
    enable_web_search = st.toggle("🌐 Bật Tìm Kiếm Web Real-time", value=False)
    
    st.write("---")
    
    if st.button("➕ Tạo cuộc trò chuyện mới", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        new_title = f"Cuộc trò chuyện {len(st.session_state.chats) + 1}"
        init_msg = "Phiên trò chuyện mới đã bắt đầu. Hãy đặt câu hỏi để AI tự động đặt tên đoạn chat nhé!"
        
        st.session_state.chats[new_title] = {
            "id": new_id,
            "messages": [{"role": "assistant", "content": init_msg, "display_content": init_msg}]
        }
        st.session_state.current_chat = new_title
        
        if hasattr(mo_hinh_ai, "save_chat_node"):
            mo_hinh_ai.save_chat_node(new_id, new_title)
            mo_hinh_ai.save_message(new_id, "assistant", init_msg, init_msg)
        st.rerun()

    chat_list = list(st.session_state.chats.keys())
    if st.session_state.current_chat not in chat_list and chat_list:
        st.session_state.current_chat = chat_list[0]
        
    selected_chat = st.radio(
        "Các đoạn chat đã lưu:", 
        chat_list, 
        index=chat_list.index(st.session_state.current_chat) if st.session_state.current_chat in chat_list else 0
    )
    
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    st.write("---")
    with st.expander("⚙️ Quản lý đoạn chat này"):
        new_title_input = st.text_input("Đổi tên đoạn chat:", value=st.session_state.current_chat)
        current_id = st.session_state.chats[st.session_state.current_chat]["id"]
        
        if st.button("💾 Lưu tên mới", use_container_width=True):
            if new_title_input.strip() and new_title_input != st.session_state.current_chat:
                st.session_state.chats[new_title_input] = st.session_state.chats.pop(st.session_state.current_chat)
                st.session_state.current_chat = new_title_input
                if hasattr(mo_hinh_ai, "update_chat_title"):
                    mo_hinh_ai.update_chat_title(current_id, new_title_input)
                st.rerun()
                
        if st.button("🗑️ Xóa đoạn chat này", use_container_width=True):
            if len(st.session_state.chats) > 1:
                if hasattr(mo_hinh_ai, "delete_chat"):
                    mo_hinh_ai.delete_chat(current_id)
                del st.session_state.chats[st.session_state.current_chat]
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                st.rerun()
            else:
                st.warning("Bạn phải giữ lại ít nhất 1 cuộc trò chuyện!")

    st.divider()
    st.title("📁 Tải Tệp Đính Kèm")
    uploaded_file = st.file_uploader("Tải tệp PDF, DOCX, XLSX, Ảnh:", type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg", "txt"])

# 5. Màn hình chính
st.title("✨ Trợ Lý Web AI Trực Tuyến")
st.caption(f"Phiên làm việc: **{st.session_state.current_chat}** | DB: **{db_status}**")

# Hiển thị lịch sử tin nhắn
active_chat_data = st.session_state.chats[st.session_state.current_chat]
active_messages = active_chat_data["messages"]
active_id = active_chat_data["id"]

for message in active_messages:
    with st.chat_message(message["role"]):
        display_text = message.get("display_content", message["content"])
        st.markdown(display_text)

# 6. Xử lý nhắn tin
if user_input := st.chat_input("Nhập câu hỏi hoặc yêu cầu AI phân tích..."):
    extracted_text_from_file = ""
    display_file_note = ""

    # Xử lý tệp đính kèm với thuật toán Smart RAG Chunking
    if uploaded_file is not None:
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()
        
        with st.spinner(f"Đang đọc và phân đoạn tệp '{file_name}'..."):
            raw_text = ""
            if file_ext == "pdf":
                raw_text = mo_hinh_ai.extract_pdf(file_bytes)
                if raw_text == "PDF_IS_SCANNED_IMAGE":
                    raw_text = f"[Tài liệu '{file_name}']: File PDF ảnh quét HSK 2."
            elif file_ext == "docx":
                raw_text = mo_hinh_ai.extract_word(file_bytes)
            elif file_ext in ["xlsx", "xls"]:
                raw_text = mo_hinh_ai.extract_excel(file_bytes)
            elif file_ext in ["png", "jpg", "jpeg"]:
                raw_text = mo_hinh_ai.analyze_image(file_bytes)
            elif file_ext == "txt":
                raw_text = uploaded_file.getvalue().decode("utf-8")
        
            # Trích xuất đoạn phù hợp nhất (Light RAG Chunking)
            if raw_text and raw_text != "PDF_IS_SCANNED_IMAGE":
                extracted_text_from_file = mo_hinh_ai.retrieve_relevant_chunks(raw_text, user_input)
            else:
                extracted_text_from_file = raw_text

        display_file_note = f"\n\n📎 *Đã đính kèm: `{file_name}`*"

    # Tra cứu Web Real-time nếu được bật
    web_search_context = ""
    if enable_web_search:
        with st.spinner(f"🌐 Đang tra cứu thông tin Web real-time cho '{user_input}'..."):
            web_search_context = mo_hinh_ai.search_web(user_input)

    if extracted_text_from_file:
        full_api_prompt = f"Dưới đây là nội dung đính kèm từ tệp '{uploaded_file.name}':\n\n{extracted_text_from_file}\n\n---\nYêu cầu: {user_input}"
    else:
        full_api_prompt = user_input

    display_prompt = user_input + display_file_note
    if enable_web_search and web_search_context:
        display_prompt += "\n\n🌐 *[Đã tra cứu dữ liệu Web real-time]*"

    # Hiển thị câu hỏi người dùng
    with st.chat_message("user"):
        st.markdown(display_prompt)

    # Lưu tin nhắn người dùng
    active_messages.append({"role": "user", "content": full_api_prompt, "display_content": display_prompt})
    if hasattr(mo_hinh_ai, "save_message"):
        mo_hinh_ai.save_message(active_id, "user", full_api_prompt, display_prompt)

    # --- ĐẶT TÊN TỰ ĐỘNG NẾU LÀ CÂU HỎI ĐẦU TIÊN ---
    user_msg_count = sum(1 for m in active_messages if m["role"] == "user")
    if user_msg_count == 1 and ("Cuộc trò chuyện" in st.session_state.current_chat or "Cuộc trò chuyện mới" in st.session_state.current_chat):
        new_auto_title = mo_hinh_ai.generate_chat_title(user_input)
        if new_auto_title and new_auto_title != st.session_state.current_chat:
            st.session_state.chats[new_auto_title] = st.session_state.chats.pop(st.session_state.current_chat)
            st.session_state.current_chat = new_auto_title
            if hasattr(mo_hinh_ai, "update_chat_title"):
                mo_hinh_ai.update_chat_title(active_id, new_auto_title)

    clean_history_for_api = [{"role": m["role"], "content": m["content"]} for m in active_messages]

    # Hiệu ứng gõ chữ thời gian thực
    with st.chat_message("assistant"):
        stream_generator = mo_hinh_ai.chat_stream(clean_history_for_api, web_search_context=web_search_context)
        phan_hoi_ai = st.write_stream(stream_generator)

    # Lưu tin nhắn trả lời của AI
    active_messages.append({"role": "assistant", "content": phan_hoi_ai, "display_content": phan_hoi_ai})
    if hasattr(mo_hinh_ai, "save_message"):
        mo_hinh_ai.save_message(active_id, "assistant", phan_hoi_ai, phan_hoi_ai)
