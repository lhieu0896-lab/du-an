import streamlit as st
import io
import uuid
from ai_engine import DongCoAI

# Cấu hình trang web
st.set_page_config(
    page_title="NEXUS AI - Trợ Lý Thông Minh",
    page_icon="🧠",
    layout="wide"
)

# Khởi tạo động cơ AI
mo_hinh_ai = DongCoAI()
trang_thai_db = getattr(mo_hinh_ai, "trang_thai_db", "CHƯA_KẾT_NỐI")

# Khởi tạo bộ nhớ phiên làm việc
if "nguoi_dung" not in st.session_state:
    st.session_state.nguoi_dung = None

# =====================================================================
# MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ
# =====================================================================
if st.session_state.nguoi_dung is None:
    st.title("🧠 NEXUS AI - Hệ Thống Trí Tuệ Nhóm")
    st.caption("Đăng nhập hoặc đăng ký tài khoản để bảo mật lịch sử chat.")
    st.write("---")

    the_dang_nhap, the_dang_ky = st.tabs(["🔒 Đăng Nhập", "📝 Đăng ký Tài Khoản Mới"])

    # Tab Đăng nhập
    with the_dang_nhap:
        st.subheader("Đăng nhập tài khoản")
        ten_dang_nhap_nhap = st.text_input("Tên tài khoản:", key="login_user")
        mat_khau_nhap = st.text_input("Mật khẩu:", type="password", key="login_pass")
        
        if st.button("🚀 Đăng Nhập", type="primary", use_container_width=True):
            if ten_dang_nhap_nhap and mat_khau_nhap:
                thong_tin_user, thong_bao = mo_hinh_ai.xac_thuc_dang_nhap(ten_dang_nhap_nhap, mat_khau_nhap)
                if thong_tin_user:
                    st.session_state.nguoi_dung = thong_tin_user
                    st.success(f"Xin chào {thong_tin_user['full_name']}!")
                    st.rerun()
                else:
                    st.error(thong_bao)
            else:
                st.warning("Vui lòng nhập đầy đủ Tên tài khoản và Mật khẩu!")

    # Tab Đăng ký
    with the_dang_ky:
        st.subheader("Tạo tài khoản mới")
        ho_ten_dk = st.text_input("Họ và Tên đầy đủ:", key="reg_name")
        ten_dang_nhap_dk = st.text_input("Tên tài khoản (viết liền):", key="reg_user")
        mat_khau_dk = st.text_input("Mật khẩu:", type="password", key="reg_pass")
        xac_nhan_mat_khau_dk = st.text_input("Xác nhận Mật khẩu:", type="password", key="reg_confirm")

        if st.button("✨ Tạo Tài Khoản", use_container_width=True):
            if not ho_ten_dk or not ten_dang_nhap_dk or not mat_khau_dk:
                st.warning("Vui lòng điền đầy đủ thông tin!")
            elif mat_khau_dk != xac_nhan_mat_khau_dk:
                st.error("Mật khẩu xác nhận không khớp!")
            else:
                thanh_cong, thong_bao = mo_hinh_ai.dang_ky_tai_khoan(ho_ten_dk, ten_dang_nhap_dk, mat_khau_dk)
                if thanh_cong:
                    st.success(thong_bao + " Hãy chuyển sang tab Đăng Nhập để bắt đầu.")
                else:
                    st.error(thong_bao)

    st.stop()

# =====================================================================
# GIAO DIỆN CHÁT CHÍNH (ĐÃ ĐĂNG NHẬP)
# =====================================================================
id_user_hien_tai = st.session_state.nguoi_dung["id"]
ten_user_hien_tai = st.session_state.nguoi_dung["full_name"]

# Tải lịch sử chat cá nhân từ DB
if "danh_sach_chat" not in st.session_state or getattr(st.session_state, "id_user_da_nap", None) != id_user_hien_tai:
    chats_tu_db = mo_hinh_ai.tai_danh_sach_chat_nguoi_dung(id_user_hien_tai)
    st.session_state.id_user_da_nap = id_user_hien_tai
    
    if chats_tu_db:
        st.session_state.danh_sach_chat = chats_tu_db
        st.session_state.chat_hien_tai = list(chats_tu_db.keys())[0]
    else:
        id_khoi_tao = str(uuid.uuid4())
        tieu_de_mac_dinh = "Cuộc trò chuyện mới"
        tin_nhan_khoi_tao = f"Xin chào **{ten_user_hien_tai}**! Lịch sử chat của bạn được lưu riêng biệt bảo mật trên Database."
        st.session_state.danh_sach_chat = {
            tieu_de_mac_dinh: {
                "id": id_khoi_tao,
                "messages": [
                    {"role": "assistant", "content": tin_nhan_khoi_tao, "display_content": tin_nhan_khoi_tao}
                ]
            }
        }
        st.session_state.chat_hien_tai = tieu_de_mac_dinh
        if trang_thai_db == "ĐÃ_KẾT_NỐI":
            mo_hinh_ai.luu_phien_chat(id_khoi_tao, tieu_de_mac_dinh, id_user_hien_tai)
            mo_hinh_ai.luu_tin_nhan(id_khoi_tao, "assistant", tin_nhan_khoi_tao, tin_nhan_khoi_tao)

# Sidebar công cụ
with st.sidebar:
    st.title("🧠 NEXUS AI")
    st.caption(f"👤 Tài khoản: **{ten_user_hien_tai}**")
    
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.nguoi_dung = None
        st.session_state.danh_sach_chat = {}
        st.rerun()
        
    st.write("---")
    bat_tim_web = st.toggle("🌐 Tra Cứu Web Real-time", value=True)
    st.write("---")
    
    # Tạo phiên chat mới
    if st.button("➕ Tạo phiên chat mới", use_container_width=True, type="primary"):
        id_moi = str(uuid.uuid4())
        tieu_de_moi = f"Cuộc trò chuyện {len(st.session_state.danh_sach_chat) + 1}"
        tin_nhan_khoi_tao = "Phiên trò chuyện cá nhân mới đã được khởi tạo!"
        
        st.session_state.danh_sach_chat[tieu_de_moi] = {
            "id": id_moi,
            "messages": [{"role": "assistant", "content": tin_nhan_khoi_tao, "display_content": tin_nhan_khoi_tao}]
        }
        st.session_state.chat_hien_tai = tieu_de_moi
        
        mo_hinh_ai.luu_phien_chat(id_moi, tieu_de_moi, id_user_hien_tai)
        mo_hinh_ai.luu_tin_nhan(id_moi, "assistant", tin_nhan_khoi_tao, tin_nhan_khoi_tao)
        st.rerun()

    # Danh sách chat
    danh_sach_tieu_de_chat = list(st.session_state.danh_sach_chat.keys())
    if st.session_state.chat_hien_tai not in danh_sach_tieu_de_chat and danh_sach_tieu_de_chat:
        st.session_state.chat_hien_tai = danh_sach_tieu_de_chat[0]
        
    chat_duoc_chon = st.radio(
        "Lịch sử chat cá nhân:", 
        danh_sach_tieu_de_chat, 
        index=danh_sach_tieu_de_chat.index(st.session_state.chat_hien_tai) if st.session_state.chat_hien_tai in danh_sach_tieu_de_chat else 0
    )
    
    if chat_duoc_chon != st.session_state.chat_hien_tai:
        st.session_state.chat_hien_tai = chat_duoc_chon
        st.rerun()

    st.write("---")
    with st.expander("⚙️ Quản lý & Tải Chat"):
        tieu_de_moi_nhap = st.text_input("Đổi tên đoạn chat:", value=st.session_state.chat_hien_tai)
        id_chat_hien_tai = st.session_state.danh_sach_chat[st.session_state.chat_hien_tai]["id"]
        
        if st.button("💾 Lưu tên mới", use_container_width=True):
            if tieu_de_moi_nhap.strip() and tieu_de_moi_nhap != st.session_state.chat_hien_tai:
                st.session_state.danh_sach_chat[tieu_de_moi_nhap] = st.session_state.danh_sach_chat.pop(st.session_state.chat_hien_tai)
                st.session_state.chat_hien_tai = tieu_de_moi_nhap
                mo_hinh_ai.cap_nhat_tieu_de_chat(id_chat_hien_tai, tieu_de_moi_nhap)
                st.rerun()

        # Tải file Word
        luong_word = mo_hinh_ai.xuat_chat_ra_file_word(
            st.session_state.danh_sach_chat[st.session_state.chat_hien_tai]["messages"],
            st.session_state.chat_hien_tai
        )
        st.download_button(
            label="📄 Tải Chat về File Word (.docx)",
            data=luong_word,
            file_name=f"{st.session_state.chat_hien_tai}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
                
        if st.button("🗑️ Xóa phiên chat này", use_container_width=True):
            if len(st.session_state.danh_sach_chat) > 1:
                mo_hinh_ai.xoa_phien_chat(id_chat_hien_tai)
                del st.session_state.danh_sach_chat[st.session_state.chat_hien_tai]
                st.session_state.chat_hien_tai = list(st.session_state.danh_sach_chat.keys())[0]
                st.rerun()

    st.divider()
    st.title("📁 Đính Kèm Tệp")
    tep_tai_len = st.file_uploader("Tải tệp PDF, DOCX, XLSX, Ảnh:", type=["pdf", "docx", "xlsx", "xls", "png", "jpg", "jpeg", "txt"])
    
    st.write("---")
    st.caption("⚡ **Developed by Hiếu & Team**")

# Màn hình chat chính
st.title("🧠 NEXUS AI - Trợ Lý Trí Tuệ")
st.caption(f"Phiên làm việc: **{st.session_state.chat_hien_tai}** | Người dùng: **{ten_user_hien_tai}**")

du_lieu_chat_dang_mo = st.session_state.danh_sach_chat[st.session_state.chat_hien_tai]
tin_nhan_dang_mo = du_lieu_chat_dang_mo["messages"]
id_chat_dang_mo = du_lieu_chat_dang_mo["id"]

# Render lại lịch sử nhắn tin
for tin_nhan in tin_nhan_dang_mo:
    with st.chat_message(tin_nhan["role"]):
        van_ban_hien_thi = tin_nhan.get("display_content", tin_nhan["content"])
        st.markdown(van_ban_hien_thi)

# Nhập tin nhắn
if cau_hoi_nguoi_dung := st.chat_input("Nhập câu hỏi hoặc gửi tệp đính kèm..."):
    van_ban_trich_xuat_tu_tep = ""
    ghi_chu_tep = ""

    # Xử lý tệp tải lên
    if tep_tai_len is not None:
        luong_bytes_tep = io.BytesIO(tep_tai_len.getvalue())
        ten_tep = tep_tai_len.name
        duoi_tep = ten_tep.split(".")[-1].lower()
        
        with st.spinner(f"Đang phân tích tệp '{ten_tep}'..."):
            van_ban_tho = ""
            if duoi_tep == "pdf":
                van_ban_tho = mo_hinh_ai.doc_file_pdf(luong_bytes_tep)
                if van_ban_tho == "PDF_IS_SCANNED_IMAGE":
                    van_ban_tho = f"[Tài liệu '{ten_tep}']: File PDF ảnh quét."
            elif duoi_tep == "docx":
                van_ban_tho = mo_hinh_ai.doc_file_word(luong_bytes_tep)
            elif duoi_tep in ["xlsx", "xls"]:
                van_ban_tho = mo_hinh_ai.doc_file_excel(luong_bytes_tep)
            elif duoi_tep in ["png", "jpg", "jpeg"]:
                van_ban_tho = mo_hinh_ai.phan_tich_hinh_anh(luong_bytes_tep)
            elif duoi_tep == "txt":
                van_ban_tho = tep_tai_len.getvalue().decode("utf-8")
        
            if van_ban_tho and van_ban_tho != "PDF_IS_SCANNED_IMAGE":
                van_ban_trich_xuat_tu_tep = mo_hinh_ai.trich_xuat_doan_lien_quan(van_ban_tho, cau_hoi_nguoi_dung)
            else:
                van_ban_trich_xuat_tu_tep = van_ban_tho

        ghi_chu_tep = f"\n\n📎 *Tệp đính kèm: `{ten_tep}`*"

    # Tìm kiếm Web
    ngu_canh_web = ""
    if bat_tim_web:
        with st.spinner(f"🌐 Đang tra cứu Web real-time..."):
            ngu_canh_web = mo_hinh_ai.tim_kiem_web(cau_hoi_nguoi_dung)

    if van_ban_trich_xuat_tu_tep:
        noi_dung_gui_api = f"Dưới đây là nội dung đính kèm từ tệp '{tep_tai_len.name}':\n\n{van_ban_trich_xuat_tu_tep}\n\n---\nYêu cầu: {cau_hoi_nguoi_dung}"
    else:
        noi_dung_gui_api = cau_hoi_nguoi_dung

    noi_dung_hien_thi = cau_hoi_nguoi_dung + ghi_chu_tep
    if bat_tim_web and ngu_canh_web and ngu_canh_web != "CHƯA_CÓ_KẾT_QUẢ":
        noi_dung_hien_thi += "\n\n🌐 *[Đã tự động tổng hợp dữ liệu Web real-time]*"

    with st.chat_message("user"):
        st.markdown(noi_dung_hien_thi)

    # Lưu tin nhắn người dùng
    tin_nhan_dang_mo.append({"role": "user", "content": noi_dung_gui_api, "display_content": noi_dung_hien_thi})
    mo_hinh_ai.luu_tin_nhan(id_chat_dang_mo, "user", noi_dung_gui_api, noi_dung_hien_thi)

    # Đặt tên tự động nếu là tin nhắn đầu tiên
    so_tin_nhan_user = sum(1 for m in tin_nhan_dang_mo if m["role"] == "user")
    if so_tin_nhan_user == 1 and ("Cuộc trò chuyện" in st.session_state.chat_hien_tai or "Cuộc trò chuyện mới" in st.session_state.chat_hien_tai):
        tieu_de_tu_dong = mo_hinh_ai.tao_tieu_de_chat(cau_hoi_nguoi_dung)
        if tieu_de_tu_dong and tieu_de_tu_dong != st.session_state.chat_hien_tai:
            st.session_state.danh_sach_chat[tieu_de_tu_dong] = st.session_state.danh_sach_chat.pop(st.session_state.chat_hien_tai)
            st.session_state.chat_hien_tai = tieu_de_tu_dong
            mo_hinh_ai.cap_nhat_tieu_de_chat(id_chat_dang_mo, tieu_de_tu_dong)

    lich_su_sach_gui_api = [{"role": m["role"], "content": m["content"]} for m in tin_nhan_dang_mo]

    # Render câu trả lời của AI dạng streaming
    with st.chat_message("assistant"):
        luong_phan_hoi = mo_hinh_ai.luong_phan_hoi_chat(lich_su_sach_gui_api, ngu_canh_web=ngu_canh_web)
        phan_hoi_ai = st.write_stream(luong_phan_hoi)

    # Lưu tin nhắn của AI
    tin_nhan_dang_mo.append({"role": "assistant", "content": phan_hoi_ai, "display_content": phan_hoi_ai})
    mo_hinh_ai.luu_tin_nhan(id_chat_dang_mo, "assistant", phan_hoi_ai, phan_hoi_ai)
