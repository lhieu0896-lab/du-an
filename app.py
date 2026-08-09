# -*- coding: utf-8 -*-
import streamlit as st
import io
import uuid
from ai_engine import DongCoAI

# Cấu hình trang giao diện Web
st.set_page_config(page_title="NEXUS AI - Trợ Lý Thông Minh", page_icon="🧠", layout="wide")

# Khởi tạo động cơ Backend AI
@st.cache_resource
def nap_dong_co():
    return DongCoAI()

mo_hinh_ai = nap_dong_co()

# Khởi tạo bộ nhớ Session State
if "tai_khoan_hien_tai" not in st.session_state:
    st.session_state.tai_khoan_hien_tai = None
if "danh_sach_phien_chat" not in st.session_state:
    st.session_state.danh_sach_phien_chat = {}
if "id_chat_hien_tai" not in st.session_state:
    st.session_state.id_chat_hien_tai = None
if "tieu_de_chat_hien_tai" not in st.session_state:
    st.session_state.tieu_de_chat_hien_tai = None

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
if not st.session_state.tai_khoan_hien_tai:
    st.title("🧠 NEXUS AI ASSISTANT")
    st.caption("Hệ thống Trợ lý Trí tuệ Nhân tạo Giáo dục & Nghiên cứu")

    tab_dn, tab_dk = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Tài Khoản"])

    with tab_dn:
        with st.form("form_dang_nhap"):
            ten_dn = st.text_input("Tên đăng nhập:")
            mat_khau = st.text_input("Mật khẩu:", type="password")
            nut_dn = st.form_submit_button("Đăng Nhập", type="primary", use_container_width=True)

            if nut_dn:
                if ten_dn and mat_khau:
                    user, thong_bao = mo_hinh_ai.xac_thuc_dang_nhap(ten_dn, mat_khau)
                    if user:
                        st.session_state.tai_khoan_hien_tai = user
                        # Nạp danh sách chat cá nhân hóa từ Supabase
                        chats_db = mo_hinh_ai.tai_danh_sach_chat_nguoi_dung(user["id"])
                        st.session_state.danh_sach_phien_chat = chats_db
                        st.success(thong_bao)
                        st.rerun()
                    else:
                        st.error(thong_bao)
                else:
                    st.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")

    with tab_dk:
        with st.form("form_dang_ky"):
            ho_ten = st.text_input("Họ và tên:")
            ten_dn_moi = st.text_input("Tên đăng nhập mới:")
            mat_khau_moi = st.text_input("Mật khẩu mới:", type="password")
            nut_dk = st.form_submit_button("Tạo Tài Khoản", use_container_width=True)

            if nut_dk:
                if ho_ten and ten_dn_moi and mat_khau_moi:
                    ok, thong_bao = mo_hinh_ai.dang_ky_tai_khoan(ho_ten, ten_dn_moi, mat_khau_moi)
                    if ok:
                        st.success(thong_bao)
                    else:
                        st.error(thong_bao)
                else:
                    st.warning("Vui lòng điền đủ thông tin để đăng ký!")

# --- GIAO DIỆN CHÁT CHÍNH SAU KHU ĐĂNG NHẬP ---
else:
    user = st.session_state.tai_khoan_hien_tai

    # 1. THANH SIDEBAR QUẢN LÝ
    with st.sidebar:
        st.title("👤 TÀI KHOẢN")
        st.write(f"**Họ tên:** {user.get('full_name', 'Người dùng')}")
        st.write(f"**Username:** `{user.get('username')}`")
        
        st.divider()

        # Nút tạo phiên chat mới
        if st.button("➕ Đoạn chat mới", use_container_width=True, type="primary"):
            st.session_state.id_chat_hien_tai = None
            st.session_state.tieu_de_chat_hien_tai = None
            st.rerun()

        st.divider()
        st.subheader("📜 Lịch sử trò chuyện")

        # Danh sách các phiên chat cũ
        for tieu_de, du_lieu in list(st.session_state.danh_sach_phien_chat.items()):
            col_phien, col_xoa = st.columns([4, 1])
            if col_phien.button(f"💬 {tieu_de}", key=f"btn_{du_lieu['id']}", use_container_width=True):
                st.session_state.id_chat_hien_tai = du_lieu["id"]
                st.session_state.tieu_de_chat_hien_tai = tieu_de
                st.rerun()

            if col_xoa.button("❌", key=f"del_{du_lieu['id']}"):
                mo_hinh_ai.xoa_phien_chat(du_lieu["id"])
                del st.session_state.danh_sach_phien_chat[tieu_de]
                if st.session_state.id_chat_hien_tai == du_lieu["id"]:
                    st.session_state.id_chat_hien_tai = None
                    st.session_state.tieu_de_chat_hien_tai = None
                st.rerun()

        st.divider()

        # Công tắc bật/tắt tìm kiếm Web Real-time
        bat_tim_kiem_web = st.toggle("🌐 Tra cứu Web Real-time", value=False)

        # Bộ tải tệp đính kèm
        tep_dinh_kem = st.file_uploader(
            "📌 Đính kèm tệp (PDF, Word, Excel, Ảnh):",
            type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg"]
        )

        st.divider()

        # Xuất báo cáo Word nếu phiên chat hiện tại có dữ liệu
        if st.session_state.tieu_de_chat_hien_tai in st.session_state.danh_sach_phien_chat:
            tin_nhan_hien_tai = st.session_state.danh_sach_phien_chat[st.session_state.tieu_de_chat_hien_tai]["messages"]
            if tin_nhan_hien_tai:
                file_word = mo_hinh_ai.xuat_chat_ra_file_word(tin_nhan_hien_tai, st.session_state.tieu_de_chat_hien_tai)
                st.download_button(
                    label="📄 Tải Chat về File Word (.docx)",
                    data=file_word,
                    file_name=f"BaoCao_{st.session_state.tieu_de_chat_hien_tai}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.tai_khoan_hien_tai = None
            st.session_state.danh_sach_phien_chat = {}
            st.session_state.id_chat_hien_tai = None
            st.session_state.tieu_de_chat_hien_tai = None
            st.rerun()

    # 2. KHUNG CHÁT CHÍNH (MAIN CHAT AREA)
    st.title("🧠 NEXUS AI ASSISTANT")

    # Xác định lịch sử tin nhắn của phiên hiện tại
    if st.session_state.tieu_de_chat_hien_tai and st.session_state.tieu_de_chat_hien_tai in st.session_state.danh_sach_phien_chat:
        lich_su_tin_nhan = st.session_state.danh_sach_phien_chat[st.session_state.tieu_de_chat_hien_tai]["messages"]
    else:
        lich_su_tin_nhan = []

    # Hiển thị lịch sử trò chuyện
    for tin in lich_su_tin_nhan:
        with st.chat_message(tin["role"]):
            st.write(tin.get("display_content", tin["content"]))

    # Ô nhập câu hỏi từ người dùng
    cau_hoi_nguoi_dung = st.chat_input("Nhập câu hỏi hoặc đính kèm tệp ở thanh bên...")

    if cau_hoi_nguoi_dung or tep_dinh_kem:
        if not cau_hoi_nguoi_dung and tep_dinh_kem:
            cau_hoi_nguoi_dung = f"Hãy đọc và phân tích nội dung tệp đính kèm '{tep_dinh_kem.name}' này giúp tôi."

        # Xử lý nếu đây là câu hỏi đầu tiên của phiên chat mới
        if not st.session_state.id_chat_hien_tai:
            id_chat_moi = str(uuid.uuid4())
            tieu_de_moi = mo_hinh_ai.tao_tieu_de_chat(cau_hoi_nguoi_dung)
            
            st.session_state.id_chat_hien_tai = id_chat_moi
            st.session_state.tieu_de_chat_hien_tai = tieu_de_moi
            
            st.session_state.danh_sach_phien_chat[tieu_de_moi] = {
                "id": id_chat_moi,
                "messages": []
            }
            # Lưu phiên chat lên Supabase
            mo_hinh_ai.luu_phien_chat(id_chat_moi, tieu_de_moi, user["id"])

        # Đọc nội dung tệp đính kèm nếu có
        noi_dung_tep = ""
        noi_dung_hien_thi = cau_hoi_nguoi_dung

        if tep_dinh_kem:
            duoi_file = tep_dinh_kem.name.split(".")[-1].lower()
            bytes_file = io.BytesIO(tep_dinh_kem.getvalue())

            if duoi_file == "pdf":
                noi_dung_tep = mo_hinh_ai.doc_file_pdf(bytes_file)
            elif duoi_file == "docx":
                noi_dung_tep = mo_hinh_ai.doc_file_word(bytes_file)
            elif duoi_file in ["xlsx", "xls"]:
                noi_dung_tep = mo_hinh_ai.doc_file_excel(bytes_file)
            elif duoi_file in ["png", "jpg", "jpeg"]:
                noi_dung_tep = mo_hinh_ai.phan_tich_hinh_anh(bytes_file, cau_hoi_nguoi_dung)

            if noi_dung_tep and duoi_file != "png" and duoi_file != "jpg" and duoi_file != "jpeg":
                # Lọc RAG nhẹ nếu tài liệu dài
                doan_trich = mo_hinh_ai.trich_xuat_doan_lien_quan(noi_dung_tep, cau_hoi_nguoi_dung)
                noi_dung_gui_ai = f"{cau_hoi_nguoi_dung}\n\n[NỘI DUNG TỆP ĐÍNH KÈM '{tep_dinh_kem.name}']:\n{doan_trich}"
                noi_dung_hien_thi = f"📎 **Tệp:** `{tep_dinh_kem.name}`\n\n💬 **Câu hỏi:** {cau_hoi_nguoi_dung}"
            else:
                noi_dung_gui_ai = cau_hoi_nguoi_dung
        else:
            noi_dung_gui_ai = cau_hoi_nguoi_dung

        # 1. Hiển thị tin nhắn người dùng
        with st.chat_message("user"):
            st.write(noi_dung_hien_thi)

        # Lưu tin nhắn người dùng vào bộ nhớ & Supabase
        st.session_state.danh_sach_phien_chat[st.session_state.tieu_de_chat_hien_tai]["messages"].append({
            "role": "user",
            "content": noi_dung_gui_ai,
            "display_content": noi_dung_hien_thi
        })
        mo_hinh_ai.luu_tin_nhan(st.session_state.id_chat_hien_tai, "user", noi_dung_gui_ai, noi_dung_hien_thi)

        # 2. Xử lý tìm kiếm web nếu công tắc được bật
        ngu_canh_web = ""
        if bat_tim_kiem_web:
            with st.spinner("🔍 Đang cào dữ liệu Web Real-time..."):
                ngu_canh_web = mo_hinh_ai.tim_kiem_web(cau_hoi_nguoi_dung)

        # 3. Tạo luồng phản hồi cho AI (Streaming)
        with st.chat_message("assistant"):
            # Chuẩn hóa lịch sử tin nhắn sạch gửi cho Groq
            lich_su_sach = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.danh_sach_phien_chat[st.session_state.tieu_de_chat_hien_tai]["messages"]
            ]
            
            duyet_luong = mo_hinh_ai.luong_phan_hoi_chat(lich_su_sach, ngu_canh_web)
            phan_hoi_ai = st.write_stream(duyet_luong)

        # Lưu tin nhắn AI vào bộ nhớ & Supabase
        st.session_state.danh_sach_phien_chat[st.session_state.tieu_de_chat_hien_tai]["messages"].append({
            "role": "assistant",
            "content": phan_hoi_ai,
            "display_content": phan_hoi_ai
        })
        mo_hinh_ai.luu_tin_nhan(st.session_state.id_chat_hien_tai, "assistant", phan_hoi_ai, phan_hoi_ai)
        
        st.rerun()
