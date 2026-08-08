import streamlit as st
import pandas as pd
import docx
from pypdf import PdfReader
from ai_engine import AIEngine 

# 1. Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="Bộ Công Cụ Xử Lý Văn Bản & Trợ Lý Học Tập AI", 
    page_icon="⚡",
    layout="wide"
)

# 2. Lưu mô hình AI vào bộ nhớ đệm RAM
@st.cache_resource
def tai_mo_hinh_ai():
    return AIEngine()

def doc_file_pdf(tep_tin):
    trich_xuat = PdfReader(tep_tin)
    return "\n".join([trang.extract_text() for trang in trich_xuat.pages if trang.extract_text()])

def doc_file_word(tep_tin):
    tai_lieu = docx.Document(tep_tin)
    return "\n".join([doan_van.text for doan_van in tai_lieu.paragraphs if doan_van.text.strip()])

# Khởi tạo mô hình AI
mo_hinh_ai = tai_mo_hinh_ai()

# 3. Thanh Menu cố định bên trái
with st.sidebar:
    try: 
        st.image("logo.png", width=120)
    except: 
        st.title("🛡️ NCKH")
    st.markdown("### **Hệ Thống Đa Công Cụ AI**")
    st.write("📌 **Dự án:** Xử lý Ngôn ngữ Tự nhiên & Trợ lý Tra cứu Học tập")
    st.divider()

# 4. Cột Tiêu đề
cot_logo, cot_tieu_de = st.columns([1, 6])
with cot_logo:
    try: 
        st.image("logo.png", width=90)
    except: 
        st.markdown("# ⚡")

with cot_tieu_de:
    st.markdown('<div class="tieu-de-ung-dung">Bộ Công Cụ Xử Lý Văn Bản & Trợ Lý Học Tập AI</div>', unsafe_allow_html=True)
    st.caption("Tóm tắt, Phân loại, NER, Sắc thái & Trợ lý Tra cứu Học tập Tự động")

# 5. Hàm kích hoạt Theme chuẩn tương phản cao + Icon Tĩnh & Hiệu ứng sinh động
def kich_hoat_theme(bg_color, accent_color, text_color, icons_list, static_banner_html, toast_msg, toast_icon):
    items_html = "".join([f'<div class="item-bay">{icon}</div>' for icon in icons_list])
    
    css_code = f"""
        <style>
        * {{
            transition: background-color 0.6s ease-in-out, color 0.6s ease-in-out !important;
        }}
        
        .icon-bay-container {{ 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            pointer-events: none; z-index: 9999; overflow: hidden; 
        }}
        .item-bay {{ 
            position: absolute; bottom: -60px; font-size: 2.2rem; 
            animation: bayUp 7s linear infinite; opacity: 0.85; 
            filter: drop-shadow(0px 2px 6px rgba(0,0,0,0.3));
        }}
        .item-bay:nth-child(1) {{ left: 8%; animation-delay: 0s; }}
        .item-bay:nth-child(2) {{ left: 28%; animation-delay: 1.5s; }}
        .item-bay:nth-child(3) {{ left: 48%; animation-delay: 3s; }}
        .item-bay:nth-child(4) {{ left: 68%; animation-delay: 0.8s; }}
        .item-bay:nth-child(5) {{ left: 88%; animation-delay: 2.3s; }}
        
        @keyframes bayUp {{
            0% {{ transform: translateY(0) rotate(0deg) scale(0.8); opacity: 0.2; }}
            20% {{ opacity: 0.9; }}
            80% {{ opacity: 0.9; }}
            100% {{ transform: translateY(-120vh) rotate(360deg) scale(1.2); opacity: 0; }}
        }}
        
        @keyframes popUpAnimation {{
            0% {{ transform: scale(0.85) translateY(30px); opacity: 0; }}
            70% {{ transform: scale(1.03) translateY(-5px); opacity: 1; }}
            100% {{ transform: scale(1) translateY(0); opacity: 1; }}
        }}
        
        .theme-banner-box {{
            animation: popUpAnimation 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            background: rgba(255, 255, 255, 0.95);
            border: 3px solid {accent_color};
            border-radius: 20px;
            padding: 18px 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .theme-banner-icon {{
            font-size: 3.5rem;
            filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.2));
            animation: pulseIcon 2s infinite ease-in-out;
        }}
        
        @keyframes pulseIcon {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        .theme-banner-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #0f172a !important;
            margin: 0;
        }}
        .theme-banner-desc {{
            font-size: 1rem;
            color: #475569 !important;
            margin: 0;
        }}

        .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], section[data-testid="stSidebar"] > div {{ 
            background-color: {bg_color} !important; 
        }}
        .tieu-de-ung-dung {{ font-size: 2.3rem; font-weight: 800; color: {accent_color} !important; }}
        
        .stMarkdown, .stText, p, span, li, h1, h2, h3, h4 {{ 
            color: {text_color} !important; 
            font-size: 1.05rem !important;
            line-height: 1.6 !important;
        }}
        
        div[data-testid="stAlert"] {{
            animation: popUpAnimation 0.7s ease-out forwards;
            background-color: #ffffff !important;
            border: 2px solid {accent_color} !important;
            border-radius: 14px !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.18) !important;
        }}
        div[data-testid="stAlert"] * {{
            color: #0f172a !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
        }}
        
        div[data-testid="stMetric"], .stTextArea textarea, div[data-testid="stFileUploader"], div[data-baseweb="select"], div[data-baseweb="input"] {{ 
            background-color: #ffffff !important; border: 2px solid {accent_color} !important; 
            color: #0f172a !important; border-radius: 16px !important;
        }}
        div.stButton > button {{ 
            background-color: {accent_color} !important; color: #0f172a !important; 
            font-weight: 800 !important; border-radius: 24px !important; border: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }}
        </style>
        
        <div class="icon-bay-container">
            {items_html}
        </div>
    """
    st.markdown(css_code, unsafe_allow_html=True)
    st.markdown(static_banner_html, unsafe_allow_html=True)
    st.toast(toast_msg, icon=toast_icon)

# 6. Hàm kiểm tra văn bản để tự chuyển 15 Theme chuẩn xác 100%
def tu_dong_chuyen_theme(van_ban_phan_tich):
    text_check = van_ban_phan_tich.lower()
    
    # 1. NGỮ VĂN & TÁC PHẨM (Ưu tiên hàng đầu)
    if any(tk in text_check for tk in ["ngữ văn", "văn học", "tác phẩm", "tiểu thuyết", "truyện ngắn", "thơ ca", "tác giả", "nhân vật", "tắt đèn", "chị dậu", "nam cao", "ngô tất tố", "vũ trọng phụng", "truyện kiều", "độc giả", "phân tích tác phẩm"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">📜📚</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Ngữ Văn & Tác Phẩm Văn Học</div>
                <div class="theme-banner-desc">Thư cổ, sách kinh điển và phân tích nghệ thuật ngôn từ của các tác giả.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#451a03", "#fde047", "#ffffff", ["📚", "✍️", "📖", "🍂", "📜"], banner, "Kích hoạt Theme Ngữ văn!", "📚")

    # 2. CÔNG NGHỆ & LẬP TRÌNH (IT)
    elif any(tk in text_check for tk in ["lập trình", "phần mềm", "python", "c++", "thuật toán", "trí tuệ nhân tạo", "database", "server", "github", "mạng máy tính", "mã nguồn"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">💻🤖</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Công Nghệ & Lập Trình (IT)</div>
                <div class="theme-banner-desc">Hệ thống mã nguồn, thuật toán, trí tuệ nhân tạo và cơ sở dữ liệu.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#0f172a", "#38bdf8", "#ffffff", ["💻", "🤖", "⚡", "🖥️", "⚙️"], banner, "Kích hoạt Theme Công nghệ!", "💻")

    # 3. KINH TẾ & TÀI CHÍNH
    elif any(tk in text_check for tk in ["phạm nhật vượng", "vinfast", "vingroup", "kinh tế", "doanh nhân", "doanh nghiệp", "tài chính", "chứng khoán", "ngân hàng", "đầu tư", "lợi nhuận", "lạm phát"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">💼📈</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Kinh Tế & Tài Chính Doanh Nghiệp</div>
                <div class="theme-banner-desc">Thông tin thị trường, hoạt động doanh nghiệp, tài chính và chứng khoán.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#0f291e", "#10b981", "#ffffff", ["💼", "📈", "💵", "💎", "📊"], banner, "Kích hoạt Theme Kinh tế!", "💼")

    # 4. SINH HỌC
    elif any(tk in text_check for tk in ["quang hợp", "sinh học", "sinh vật", "tế bào", "adn", "arn", "gen", "di truyền", "thực vật", "động vật", "sinh thái", "lục lạp", "diệp lục"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🧬🌿</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Sinh Học & Hệ Sinh Thái</div>
                <div class="theme-banner-desc">Mã gen di truyền ADN, cấu trúc tế bào sống, quang hợp và sinh giới.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#14532d", "#86efac", "#ffffff", ["🧬", "🌿", "🌱", "🍃", "🧬"], banner, "Kích hoạt Theme Sinh học!", "🧬")

    # 5. HÓA HỌC
    elif any(tk in text_check for tk in ["hóa học", "phản ứng hóa học", "axit", "bazơ", "nguyên tố hóa học", "mol", "kết tủa", "oxi hóa", "electron", "bảng tuần hoàn"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🧪🔬</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Hóa Học & Phản Ứng Nguyên Tố</div>
                <div class="theme-banner-desc">Phòng thí nghiệm, biến đổi chất, liên kết hóa học và bảng tuần hoàn.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#064e3b", "#34d399", "#ffffff", ["🧪", "🔬", "🫧", "⚗️", "🧪"], banner, "Kích hoạt Theme Hóa học!", "🧪")

    # 6. LỊCH SỬ CỔ ĐIỂN
    elif any(tk in text_check for tk in ["lịch sử", "30/4", "2/9", "chiến tranh", "kháng chiến", "điện biên phủ", "triều đại", "bảo tàng", "di tích lịch sử", "sử học"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🏛️📜</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Lịch Sử Cổ Điển & Bảng Vàng Sử Sách</div>
                <div class="theme-banner-desc">Không gian bảo tàng hoài niệm, trích xuất tư liệu di tích và sự kiện lịch sử.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#2b1b17", "#d97706", "#ffffff", ["🏛️", "📜", "📜", "⏳", "🥁"], banner, "Kích hoạt Theme Lịch sử!", "📜")

    # 7. TOÁN HỌC
    elif any(tk in text_check for tk in ["toán học", "đại số", "hình học", "phương trình", "định lý", "pytago", "tích phân", "đạo hàm", "số học", "ma trận"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">📐🧮</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Toán Học & Không Gian Số</div>
                <div class="theme-banner-desc">Bảng đen phấn trắng, các định lý, công thức đại số và mô hình hình học.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#1b3022", "#a3e635", "#ffffff", ["📐", "🧮", "📏", "♾️", "📐"], banner, "Kích hoạt Theme Toán học!", "📐")

    # 8. VẬT LÝ
    elif any(tk in text_check for tk in ["vật lý", "vật lí", "vận tốc", "gia tốc", "chuyển động", "điện trường", "thấu kính", "áp suất", "trọng lực", "bán dẫn"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">👨‍🔬⚛️</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Vật Lý & Cơ Học Vũ Trụ</div>
                <div class="theme-banner-desc">Mô hình nguyên tử, quy luật vận động, lực học và hiện tượng vật lý.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#0b132b", "#64dfdf", "#ffffff", ["⚡", "⚛️", "💡", "🧲", "⚡"], banner, "Kích hoạt Theme Vật lý!", "⚡")

    # 9. ĐỊA LÝ
    elif any(tk in text_check for tk in ["địa lý", "địa lí", "khí hậu", "địa hình", "bản đồ", "dân số", "thời tiết", "đại dương", "lục địa", "thủy văn"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🌍🗺️</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Địa Lý & Quả Địa Cầu</div>
                <div class="theme-banner-desc">Bản đồ địa hình, khí hậu các châu lục và các hiện tượng tự nhiên.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#0c4a6e", "#38bdf8", "#ffffff", ["🌍", "☀️", "🗺️", "⛰️", "🌍"], banner, "Kích hoạt Theme Địa lý!", "🌍")

    # 10. NGHỆ THUẬT & ÂM NHẠC
    elif any(tk in text_check for tk in ["âm nhạc", "hội họa", "nghệ thuật", "ca khúc", "bức tranh", "triển lãm", "nhạc sĩ", "họa sĩ", "giai điệu", "nhạc cụ"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🎨🎶</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Nghệ Thuật & Âm Nhạc</div>
                <div class="theme-banner-desc">Giai điệu âm nhạc, tác phẩm hội họa và sáng tác nghệ thuật.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#3b0764", "#f472b6", "#ffffff", ["🎨", "🎶", "🎵", "🎸", "🖌️"], banner, "Kích hoạt Theme Nghệ thuật!", "🎨")

    # 11. PHÁP LUẬT
    elif any(tk in text_check for tk in ["pháp luật", "hiến pháp", "bộ luật", "tòa án", "luật sư", "quyền công dân", "hình sự", "dân sự", "nghị định"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">⚖️📜</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Pháp Luật & Tư Pháp</div>
                <div class="theme-banner-desc">Hệ thống văn bản quy phạm pháp luật, hiến pháp và quyền công dân.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#1e1b4b", "#eab308", "#ffffff", ["⚖️", "📜", "🏛️", "⚖️", "📜"], banner, "Kích hoạt Theme Pháp luật!", "⚖️")

    # 12. Y HỌC & SỨC KHỎE
    elif any(tk in text_check for tk in ["y học", "bệnh viện", "bác sĩ", "dinh dưỡng", "sức khỏe", "thể thao", "bóng đá", "cầu lông", "tập luyện", "vitamin"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🏥⚽</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Y Học & Sức Khỏe Thể Thao</div>
                <div class="theme-banner-desc">Kiến thức y học, chế độ dinh dưỡng, sức khỏe và luyện tập thể thao.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#134e4a", "#2dd4bf", "#ffffff", ["🏥", "⚽", "💊", "🩺", "🏃"], banner, "Kích hoạt Theme Y học & Thể thao!", "🏥")

    # 13. ẨM THỰC & DU LỊCH
    elif any(tk in text_check for tk in ["ẩm thực", "món ăn", "nấu ăn", "nhà hàng", "du lịch", "khách sạn", "đặc sản", "điểm đến"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🍳✈️</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Ẩm Thực & Trải Nghiệm Du Lịch</div>
                <div class="theme-banner-desc">Văn hóa ẩm thực, món ăn vùng miền và các hành trình khám phá du lịch.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#431407", "#fb923c", "#ffffff", ["🍳", "✈️", "🍕", "🧳", "🥐"], banner, "Kích hoạt Theme Ẩm thực & Du lịch!", "🍳")

    # 14. THIÊN VĂN & VŨ TRỤ
    elif any(tk in text_check for tk in ["thiên văn", "hành tinh", "sao hỏa", "mặt trăng", "hố đen", "ngân hà", "kính thiên văn", "phi hành gia", "nasa"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🌌🪐</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Thiên Văn Học & Vũ Trụ</div>
                <div class="theme-banner-desc">Khám phá các hành tinh, thiên thể, dải ngân hà và bí ẩn vũ trụ.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#180b2b", "#c084fc", "#ffffff", ["🌌", "🪐", "⭐", "🚀", "🛸"], banner, "Kích hoạt Theme Thiên văn!", "🌌")

    # 15. GIẢI TRÍ & GAMING
    elif any(tk in text_check for tk in ["đấu trường chân lý", "tft", "minecraft", "game", "trò chơi", "phim ảnh", "điện ảnh", "hollywood", "streamer"]):
        banner = """
        <div class="theme-banner-box">
            <div class="theme-banner-icon">🎮🎬</div>
            <div>
                <div class="theme-banner-title">Chủ Đề: Giải Trí, Gaming & Điện Ảnh</div>
                <div class="theme-banner-desc">Thế giới trò chơi điện tử, esports, tác phẩm điện ảnh và truyền thông giải trí.</div>
            </div>
        </div>
        """
        kich_hoat_theme("#450a0a", "#f87171", "#ffffff", ["🎮", "🎬", "🕹️", "🍿", "🎧"], banner, "Kích hoạt Theme Giải trí & Gaming!", "🎮")

# 7. Tạo Tab giao diện
the_tab1, the_tab2 = st.tabs(["🚀 Bàn Làm Việc AI", "📊 Đánh Giá Tập Dữ Liệu"])

with the_tab1:
    cot_trai, cot_phai = st.columns([2, 1])
    
    with cot_trai:
        kieu_dau_vao = st.radio("Nguồn dữ liệu đầu vào:", ["Dán văn bản trực tiếp", "Tải lên Tệp (PDF / Word)"], horizontal=True)
        van_ban_dau_vao = ""
        
        if kieu_dau_vao == "Dán văn bản trực tiếp":
            van_ban_dau_vao = st.text_area("Nội dung bài học (Có thể bỏ trống nếu chọn Trợ lý tra cứu tự động):", height=240, placeholder="Dán đoạn văn bản tài liệu vào đây...")
        else:
            tep_tai_len = st.file_uploader("Tải lên tệp tài liệu học tập:", type=["pdf", "docx"])
            if tep_tai_len is not None:
                try:
                    if tep_tai_len.name.endswith(".pdf"): 
                        van_ban_dau_vao = doc_file_pdf(tep_tai_len)
                    elif tep_tai_len.name.endswith(".docx"): 
                        van_ban_dau_vao = doc_file_word(tep_tai_len)
                    st.success(f"📂 Tệp: **{tep_tai_len.name}** ({len(van_ban_dau_vao.split())} từ)")
                except Exception as loi: 
                    st.error(f"Lỗi khi mở tệp: {loi}")

    with cot_phai:
        st.subheader("🛠️ Bảng Chọn Công Cụ")
        
        cong_cu_da_chon = st.selectbox(
            "Chọn tính năng AI muốn thực hiện:",
            [
                "1. Tóm tắt Văn bản Tự động",
                "2. Phân loại Chuyên mục & Sắc thái",
                "3. Trích xuất Từ khóa & Thực thể (NER)",
                "4. Trợ lý Tra cứu & Giải thích Học tập",
                "5. Chạy Toàn bộ Phân tích (Tất cả trong một)"
            ]
        )
        
        cau_hoi_tra_cuu = ""
        if "Trợ lý Tra cứu" in cong_cu_da_chon:
            cau_hoi_tra_cuu = st.text_input("Nhập câu hỏi tra cứu kiến thức:", placeholder="Ví dụ: Định lý Pytago / Quang hợp / Nguyễn Phú Trọng")

        gioi_han_tu = 100
        if "Tóm tắt" in cong_cu_da_chon or "Tất cả trong một" in cong_cu_da_chon:
            gioi_han_tu = st.slider("Giới hạn số TỪ tối đa:", 30, 500, 100, 10)
            
        nut_thuc_thi = st.button("⚡ Thực Thi Công Cụ AI", use_container_width=True)

# THỰC THI AI VÀ ĐỔI THEME DỰA TRÊN KẾT QUẢ AI TRẢ VỀ
if nut_thuc_thi:
    if not van_ban_dau_vao.strip() and "Trợ lý Tra cứu" not in cong_cu_da_chon:
        st.warning("⚠️ Vui lòng cung cấp văn bản đầu vào trước khi thực thi!")
    elif "Trợ lý Tra cứu" in cong_cu_da_chon and not van_ban_dau_vao.strip() and not cau_hoi_tra_cuu.strip():
        st.warning("⚠️ Vui lòng dán văn bản hoặc gõ câu hỏi tra cứu!")
    else:
        st.divider()
        
        # 1. Tóm tắt
        if "1. Tóm tắt" in cong_cu_da_chon:
            with st.spinner("Đang thực hiện tóm tắt..."):
                ket_qua = mo_hinh_ai.process_summary(van_ban_dau_vao, max_len=gioi_han_tu)
            tu_dong_chuyen_theme(ket_qua["summary"])
            st.markdown("### 📝 Kết quả Tóm tắt Văn bản")
            st.info(ket_qua["summary"])
            c1, c2 = st.columns(2)
            c1.metric("Thời gian xử lý", f"{ket_qua['latency']} giây")
            c2.metric("Tỷ lệ nén văn bản", f"{ket_qua['compression']}%")

        # 2. Phân loại
        elif "2. Phân loại" in cong_cu_da_chon:
            with st.spinner("Đang phân tích chuyên mục và sắc thái..."):
                ket_qua = mo_hinh_ai.process_analysis(van_ban_dau_vao)
            tu_dong_chuyen_theme(ket_qua["category"] + " " + van_ban_dau_vao)
            st.markdown("### 🏷️ Phân loại Chuyên mục & Sắc thái")
            c1, c2 = st.columns(2)
            c1.metric("Chuyên mục dự đoán", ket_qua["category"])
            c2.metric("Sắc thái cảm xúc", ket_qua["sentiment"])

        # 3. Trích xuất NER
        elif "3. Trích xuất" in cong_cu_da_chon:
            with st.spinner("Đang trích xuất từ khóa và thực thể..."):
                ket_qua = mo_hinh_ai.process_entities(van_ban_dau_vao)
            tu_dong_chuyen_theme(" ".join(ket_qua["keywords"]) + " " + van_ban_dau_vao)
            st.markdown("### 🔑 Từ khóa cốt lõi & Thực thể tên riêng (NER)")
            st.write("**Top từ khóa chính:** " + ", ".join(ket_qua["keywords"]))
            st.write("**Thực thể tên riêng phát hiện được:**")
            if ket_qua["entities"]:
                for loai_thuc_the, danh_sach_ten in ket_qua["entities"].items():
                    st.write(f"- **{loai_thuc_the}:** {', '.join(danh_sach_ten)}")
            else:
                st.caption("Không phát hiện tên riêng / địa danh cụ thể trong văn bản.")

        # 4. Trợ lý Tra cứu
        elif "4. Trợ lý Tra cứu" in cong_cu_da_chon:
            with st.spinner("Đang tra cứu dữ liệu chuẩn xác..."):
                ket_qua = mo_hinh_ai.process_learning_assistant(van_ban_dau_vao, cau_hoi=cau_hoi_tra_cuu)
            
            # KÍCH HOẠT THEME THEO NỘI DUNG AI TRẢ LỜI
            tu_dong_chuyen_theme(ket_qua["answer"])
            
            st.markdown("### 🎓 Trợ Lý Tra Cứu & Giải Thích Bài Học")
            st.caption(f"🌐 **Nguồn tri thức:** {ket_qua['source']}")
            
            if cau_hoi_tra_cuu.strip():
                st.markdown("#### 💡 Kết quả trả lời câu hỏi:")
                st.success(ket_qua["answer"])
            
            st.markdown("#### 📚 Các khái niệm học tập bóc tách được:")
            if ket_qua["key_concepts"]:
                for kc in ket_qua["key_concepts"]:
                    st.info(kc)
            else:
                st.caption("Không trích xuất được khái niệm rõ ràng.")
            
            st.metric("Thời gian tra cứu", f"{ket_qua['latency']} giây")

        # 5. Tất cả trong một
        elif "5. Chạy Toàn bộ" in cong_cu_da_chon:
            with st.spinner("Đang tổng hợp phân tích toàn bộ dữ liệu..."):
                kq_tom_tat = mo_hinh_ai.process_summary(van_ban_dau_vao, max_len=gioi_han_tu)
                kq_phan_tich = mo_hinh_ai.process_analysis(van_ban_dau_vao)
                kq_thuc_the = mo_hinh_ai.process_entities(van_ban_dau_vao)

            tu_dong_chuyen_theme(kq_tom_tat["summary"])
            st.markdown("### 🌟 Báo cáo Phân tích Toàn diện (Tất cả trong một)")
            cot_kq1, cot_kq2 = st.columns([2, 1])
            with cot_kq1:
                st.markdown("#### 📝 Bản Tóm Tắt")
                st.info(kq_tom_tat["summary"])
                st.write("**Top từ khóa bài viết:** " + ", ".join(kq_thuc_the["keywords"]))
                if kq_thuc_the["entities"]:
                    st.write("**Thực thể tên riêng:**")
                    for loai_thuc_the, danh_sach_ten in kq_thuc_the["entities"].items():
                        st.write(f"- *{loai_thuc_the}:* {', '.join(danh_sach_ten)}")
            with cot_kq2:
                st.markdown("#### 📊 Chỉ Số Phân Tích")
                st.metric("Chuyên mục", kq_phan_tich["category"])
                st.metric("Sắc thái", kq_phan_tich["sentiment"])
                st.metric("Thời gian xử lý", f"{kq_tom_tat['latency']}s")
                st.metric("Tỷ lệ nén", f"{kq_tom_tat['compression']}%")

# TAB 2: ĐÁNH GIÁ TẬP DỮ LIỆU
with the_tab2:
    st.subheader("Đánh giá Tự động trên tập dữ liệu dataset.csv")
    if st.button("Chạy Đánh Giá Dataset"):
        try:
            bang_du_lieu = pd.read_csv("dataset.csv")
            danh_sach_ket_qua = []
            thanh_tien_trinh = st.progress(0)
            
            for chi_so, hang in bang_du_lieu.iterrows():
                kq_s = mo_hinh_ai.process_summary(hang["content"], max_len=100)
                kq_a = mo_hinh_ai.process_analysis(hang["content"])
                danh_sach_ket_qua.append({
                    "Tiêu đề": hang["title"],
                    "Chuyên mục AI": kq_a["category"],
                    "Cảm xúc": kq_a["sentiment"],
                    "Thời gian (s)": kq_s["latency"],
                    "Tỷ lệ nén (%)": kq_s["compression"]
                })
                thanh_tien_trinh.progress((chi_so + 1) / len(bang_du_lieu))
                
            bang_ket_qua_df = pd.DataFrame(danh_sach_ket_qua)
            st.dataframe(bang_ket_qua_df, use_container_width=True)
            
            st.markdown("#### 📐 Thống kê Tổng hợp")
            st.write(f"- **Thời gian xử lý trung bình:** `{bang_ket_qua_df['Thời gian (s)'].mean():.2f}` giây/bài")
            st.write(f"- **Tỷ lệ nén trung bình:** `{bang_ket_qua_df['Tỷ lệ nén (%)'].mean():.1f}%`")
        except FileNotFoundError:
            st.error("❌ Không tìm thấy tệp `dataset.csv`!")
