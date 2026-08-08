import streamlit as st
import io
import uuid
from ai_engine import AIEngine

# 1. Cấu hình Trang Web
st.set_page_config(
    page_title="NEXUS AI - Trợ Lý Thông Minh",
    page_icon="🧠",
    layout="wide"
)

# 2. Khởi tạo Engine
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

mo_hinh_ai = tai_mo_hinh_ai()
db_status = getattr(mo_hinh_ai, "db_status", "CHƯA_KẾT_NỐI")

# Khởi tạo phiên làm việc người dùng
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================================
# MÀN HÌNH ĐĂNG KIỂM / ĐĂNG NHẬP (BẮT BUỘC ĐĂNG NHẬP MỚI VÀO ĐƯỢC CHAT)
# =====================================================================
if st.session_state.user is None:
    st.title("🧠 NEXUS AI - Hệ Thống Trí Tuệ Nhóm")
    st.caption("Vui lòng Đăng nhập hoặc Đăng ký tài khoản để bảo mật lịch sử chat của bạn.")
    st.write("---")

    tab_login, tab_register = st.tabs(["🔒 Đăng Nhập", "📝 Đăng ký Tài Khoản Mới"])

    # TAB ĐĂNG NHẬP
    with tab_login:
        st.subheader("Đăng nhập tài khoản")
        login_username = st.text_input("Tên tài khoản (Username):", key="login_user")
        login_password = st.text_input("Mật khẩu:", type="password", key="login_pass")
        
        if st.button("🚀 Đăng Nhập", type="primary", use_container_width=True):
            if login_username and login_password:
                user_info, msg = mo_hinh_ai.authenticate_user(login_username, login_password)
                if user_info:
                    st.session_state.user = user_info
                    st.success(f"Xin chào {user_info['full_name']}! Đang tải dữ liệu...")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Vui lòng nhập đầy đủ Tên tài khoản và Mật khẩu!")

    # TAB ĐĂNG KÝ
    with tab_register:
        st.subheader("Tạo tài khoản mới")
        reg_fullname = st.text_input("Họ và Tên đầy đủ:", key="reg_name")
        reg_username = st.text_input("Tên tài khoản (Viết liền không dấu):", key="reg_user")
        reg_password = st.text_input("Mật khẩu:", type="password", key="reg_pass")
        reg_confirm = st.text_input("Xác nhận Mật khẩu:", type="password", key="reg_confirm")

        if st.button("✨ Tạo Tài Khoản", use_container_width=True):
            if not reg_fullname or not reg_username or not reg_password:
                st.warning("Vui lòng điền đầy đủ các thông tin!")
            elif reg_password != reg_confirm:
                st.error("Mật khẩu xác nhận không khớp!")
            else:
                success, msg = mo_hinh_ai.register_user(reg_fullname, reg_username, reg_password)
                if success:
                    st.success(msg + " Hãy chuyển sang tab 'Đăng Nhập' để bắt đầu.")
                else:
                    st.error(msg)

    st.stop() # Dừng chương trình tại đây nếu chưa đăng nhập thành công

# =====================================================================
# MÀN HÌNH CHÍNH (ĐÃ ĐĂNG NHẬP THÀNH CÔNG - LƯU CHAT CÁ NHÂN RIÊNG BIỆT)
# =====================================================================
current_user_id = st.session_state.user["id"]
current_user_name = st.session_state.user["full_name"]

# Load Lịch sử trò chuyện RIÊNG của người dùng này
if "chats" not in st.session_state or getattr(st.session_state, "loaded_user_id", None) != current_user_id:
    db_chats = mo_hinh_ai.load_user_chats(current_user_id) if hasattr(mo_hinh_ai, "load_user_chats") else {}
    st.session_state.loaded_user_id = current_user_id
    
    if db_chats:
        st.session_state.chats = db_chats
        st.session_state.current_chat = list(db_chats.keys())[0]
    else:
        init_id = str(uuid.uuid4())
        default_title = "Cuộc trò chuyện mới"
        init_msg = f"Xin chào **{current_user_name}**! Lịch sử chat của bạn đã được mã hóa bảo mật riêng biệt. Không ai khác có thể xem được nội dung này."
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
            mo_hinh_ai.save_chat_node(init_id, default_title, current_user_id)
            mo_hinh_ai.save_message(init_id, "assistant", init_msg, init_msg)

# 4. Thanh Sidebar
with st.sidebar:
    st.title("🧠 NEXUS AI")
    st.caption(f"👤 Tài khoản: **{current_user_name}**")
    
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.user = None
        st.session_state.chats = {}
        st.rerun()
        
    st.write("---")
    enable_web_search = st.toggle("🌐 Bật Tra Cứu Web Real-time", value=True)
    st.write("---")
    
    if st.button("➕ Tạo phiên chat mới", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        new_title = f"Cuộc trò chuyện {len(st.session_state.chats) + 1}"
        init_msg = "Phiên trò chuyện cá nhân mới đã được khởi tạo thành công!"
        
        st.session_state.chats[new_title] = {
            "id": new_id,
            "messages": [{"role": "assistant", "content": init_msg, "display_content": init_msg}]
        }
        st.session_state.current_chat = new_title
        
        if hasattr(mo_hinh_ai, "save_chat_node"):
            mo_hinh_ai.save_chat_node(new_id, new_title, current_user_id)
            mo_hinh_ai.save_message(new_id, "assistant", init_msg, init_msg)
        st.rerun()

    chat_list = list(st.session_state.chats.keys())
    if st.session_state.current_chat not in chat_list and chat_list:
        st.session_state.current_chat = chat_list[0]
        
    selected_chat = st.radio(
        "Lịch sử chat cá nhân:", 
        chat_list, 
        index=chat_list.index(st.session_state.current_chat) if st.session_state.current_chat in chat_list else 0
    )
    
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    st.write("---")
    with st.expander("⚙️ Quản lý & Tải Chat"):
        new_title_input = st.text_input("Đổi tên đoạn chat:", value=st.session_state.current_chat)
        current_id = st.session_state.chats[st.session_state.current_chat]["id"]
        
        if st.button("💾 Lưu tên mới", use_container_width=True):
            if new_title_input.strip() and new_title_input != st.session_state.current_chat:
                st.session_state.chats[new_title_input] = st.session_state.chats.pop(st.session_state.current_chat)
                st.session_state.current_chat = new_title_input
                if hasattr(mo_hinh_ai, "update_chat_title"):
                    mo_hinh_ai.update_chat_title(current_id, new_title_input)
                st.rerun()

        # Nút Xuất File Word
        word_stream = mo_hinh_ai.export_chat_to_word(
            st.session_state.chats[st.session_state.current_chat]["messages"],
            st.session_state.current_chat
        )
        st.download_button(
            label="📄 Tải Chat về File Word (.docx)",
            data=word_stream,
            file_name=f"{st.session_state.current_chat}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
                
        if st.button("🗑️ Xóa phiên chat này", use_container_width=True):
            if len(st.session_state.chats) > 1:
                if hasattr(mo_hinh_ai, "delete_chat"):
                    mo_hinh_ai.delete_chat(current_id)
                del st.session_state.chats[st.session_state.current_chat]
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                st.rerun()

    st.divider()
    st.title("📁 Đính Kèm Tệp")
    uploaded_file = st.file_uploader("Tải tệp PDF, DOCX, XLSX, Ảnh:", type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg", "txt"])
    
    st.write("---")
    st.caption("⚡ **Developed by Hiếu & Team**")

# 5. Màn hình chính
st.title("🧠 NEXUS AI - Trợ Lý Trí Tuệ")
st.caption(f"Phiên làm việc: **{st.session_state.current_chat}** | Người dùng: **{current_user_name}**")

# Hiển thị lịch sử tin nhắn
active_chat_data = st.session_state.chats[st.session_state.current_chat]
active_messages = active_chat_data["messages"]
active_id = active_chat_data["id"]

for message in active_messages:
    with st.chat_message(message["role"]):
        display_text = message.get("display_content", message["content"])
        st.markdown(display_text)

# 6. Xử lý nhắn tin
if user_input := st.chat_input("Nhập câu hỏi hoặc gửi tệp đính kèm..."):
    extracted_text_from_file = ""
    display_file_note = ""

    if uploaded_file is not None:
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        file_name = uploaded_file.name
        file_ext = file_name.split(".")[-1].lower()
        
        with st.spinner(f"Đang phân tích tệp '{file_name}'..."):
            raw_text = ""
            if file_ext == "pdf":
                raw_text = mo_hinh_ai.extract_pdf(file_bytes)
                if raw_text == "PDF_IS_SCANNED_IMAGE":
                    raw_text = f"[Tài liệu '{file_name}']: File PDF ảnh quét."
            elif file_ext == "docx":
                raw_text = mo_hinh_ai.extract_word(file_bytes)
            elif file_ext in ["xlsx", "xls"]:
                raw_text = mo_hinh_ai.extract_excel(file_bytes)
            elif file_ext in ["png", "jpg", "jpeg"]:
                raw_text = mo_hinh_ai.analyze_image(file_bytes)
            elif file_ext == "txt":
                raw_text = uploaded_file.getvalue().decode("utf-8")
        
            if raw_text and raw_text != "PDF_IS_SCANNED_IMAGE":
                extracted_text_from_file = mo_hinh_ai.retrieve_relevant_chunks(raw_text, user_input)
            else:
                extracted_text_from_file = raw_text

        display_file_note = f"\n\n📎 *Tệp đính kèm: `{file_name}`*"

    # Tra cứu Web Real-time
    web_search_context = ""
    if enable_web_search:
        with st.spinner(f"🌐 Đang tra cứu Web real-time..."):
            web_search_context = mo_hinh_ai.search_web(user_input)

    if extracted_text_from_file:
        full_api_prompt = f"Dưới đây là nội dung đính kèm từ tệp '{uploaded_file.name}':\n\n{extracted_text_from_file}\n\n---\nYêu cầu: {user_input}"
    else:
        full_api_prompt = user_input

    display_prompt = user_input + display_file_note
    if enable_web_search and web_search_context and web_search_context != "CHƯA_CÓ_KẾT_QUẢ":
        display_prompt += "\n\n🌐 *[Đã tự động tổng hợp dữ liệu Web real-time]*"

    with st.chat_message("user"):
        st.markdown(display_prompt)

    # Lưu RAM & DB
    active_messages.append({"role": "user", "content": full_api_prompt, "display_content": display_prompt})
    if hasattr(mo_hinh_ai, "save_message"):
        mo_hinh_ai.save_message(active_id, "user", full_api_prompt, display_prompt)

    # Đặt tên tự động nếu là câu hỏi đầu tiên
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

    # Lưu RAM & DB
    active_messages.append({"role": "assistant", "content": phan_hoi_ai, "display_content": phan_hoi_ai})
    if hasattr(mo_hinh_ai, "save_message"):
        mo_hinh_ai.save_message(active_id, "assistant", phan_hoi_ai, phan_hoi_ai)
