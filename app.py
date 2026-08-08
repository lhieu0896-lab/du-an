import streamlit as st
from ai_engine import AIEngine

# 1. Cấu hình trang Web Chat
st.set_page_config(
    page_title="Trợ Lý AI Trực Tuyến",
    page_icon="🤖",
    layout="centered"
)

# 2. Khởi tạo Mô hình AI
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

mo_hinh_ai = tai_mo_hinh_ai()

# 3. Khởi tạo Bộ nhớ Lịch sử Trò chuyện (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý AI. Tôi có thể giúp gì cho bạn hôm nay?"}
    ]

# 4. Thanh Sidebar quản lý
with st.sidebar:
    st.title("⚙️ Tùy Chọn Chat")
    st.write("🤖 **Model:** Groq Llama 3.3 70B")
    st.write("🧠 **Trí nhớ:** Tự động ghi nhớ toàn bộ cuộc trò chuyện trong phiên làm việc.")
    st.divider()
    
    # Nút Xóa lịch sử để chat lại từ đầu
    if st.button("🗑️ Xóa Lịch Sử Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Lịch sử trò chuyện đã được xóa. Chúng ta bắt đầu lại nhé!"}
        ]
        st.rerun()

# 5. Tiêu đề ứng dụng Web Chat
st.title("💬 Trợ Lý AI Thông Minh")
st.caption("Hệ thống Web AI thuần túy - Có khả năng ghi nhớ ngữ cảnh cuộc trò chuyện")

# 6. Hiển thị tất cả các tin nhắn cũ từ bộ nhớ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Ô nhập liệu tin nhắn mới từ người dùng
if user_input := st.chat_input("Nhập câu hỏi hoặc trò chuyện với AI..."):
    # Hiển thị ngay tin nhắn của người dùng lên màn hình
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Lưu tin nhắn của người dùng vào bộ nhớ
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Gọi AI xử lý kèm theo toàn bộ bộ nhớ ngữ cảnh
    with st.chat_message("assistant"):
        with st.spinner("AI đang suy nghĩ..."):
            # Lấy danh sách tin nhắn lịch sử (chỉ lấy role và content)
            history_for_api = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            phan_hoi_ai = mo_hinh_ai.chat_with_memory(history_for_api)
            st.markdown(phan_hoi_ai)

    # Lưu câu trả lời của AI vào bộ nhớ lịch sử
    st.session_state.messages.append({"role": "assistant", "content": phan_hoi_ai})
