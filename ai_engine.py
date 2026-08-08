# -*- coding: utf-8 -*-
import sys
import os
import time
import re
from collections import Counter
from underthesea import classify, sentiment, ner, pos_tag
from groq import Groq

# Ép hệ thống dùng chuẩn UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AIEngine:
    def __init__(self):
        print("Khởi tạo hệ thống xử lý ngôn ngữ tự nhiên AI...")
        # Lấy API Key từ Secrets của Streamlit Cloud hoặc Biến môi trường
        self.api_key = os.getenv("GROQ_API_KEY", "")
        
        # Nếu không thấy trong os.getenv, thử đọc trực tiếp từ st.secrets của Streamlit
        if not self.api_key:
            try:
                import streamlit as st
                if "GROQ_API_KEY" in st.secrets:
                    self.api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass

        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            
        self.model_name = "llama-3.3-70b-versatile"

    def _lam_sach_van_ban(self, van_ban):
        if not van_ban:
            return ""
        van_ban_str = str(van_ban)
        return re.sub(r'\s+', ' ', van_ban_str).strip()

    # 1. TÍNH NĂNG TÓM TẮT VĂN BẢN
    def process_summary(self, van_ban, max_len=100):
        thoi_gian_bat_dau = time.time()
        text_sach = self._lam_sach_van_ban(van_ban)
        
        if not text_sach:
            return {"summary": "Không có văn bản đầu vào.", "latency": 0.0, "compression": 0.0}

        try:
            if not self.client:
                raise Exception("Chưa cấu hình GROQ_API_KEY")

            prompt = f"Hãy tóm tắt đoạn văn bản sau bằng tiếng Việt thật mượt mà, cô đọng dưới {max_len} từ:\n\n{text_sach}"
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.3
            )
            van_ban_tom_tat = response.choices[0].message.content.strip()
        except Exception:
            danh_sach_cau = [c.strip() for c in re.split(r'(?<=[.!?])\s+', text_sach) if len(c.strip()) > 10]
            if len(danh_sach_cau) <= 2:
                van_ban_tom_tat = text_sach
            else:
                cac_tu = [w.lower() for w in re.findall(r'\w+', text_sach) if len(w) > 2]
                tan_suat_tu = Counter(cac_tu)
                cau_duoc_cham_diem = []

                for chi_so, cau in enumerate(danh_sach_cau):
                    diem_so = sum([tan_suat_tu.get(w.lower(), 0) for w in re.findall(r'\w+', cau) if len(w) > 2])
                    if chi_so == 0: diem_so *= 1.8
                    elif chi_so == len(danh_sach_cau) - 1: diem_so *= 1.4
                    cau_duoc_cham_diem.append({"id": chi_so, "score": diem_so, "text": cau, "words": cau.split()})

                cau_xep_hang = sorted(cau_duoc_cham_diem, key=lambda x: x["score"], reverse=True)
                cau_duoc_chon = []
                tong_so_tu = 0

                for item in cau_xep_hang:
                    if tong_so_tu + len(item["words"]) <= max_len:
                        cau_duoc_chon.append(item)
                        tong_so_tu += len(item["words"])
                    elif not cau_duoc_chon:
                        cau_duoc_chon.append(item)
                        break

                cau_duoc_chon.sort(key=lambda x: x["id"])
                van_ban_tom_tat = " ".join([item["text"] for item in cau_duoc_chon])

        thoi_gian_xuly = round(time.time() - thoi_gian_bat_dau, 2)
        so_tu_goc = len(text_sach.split())
        so_tu_tom_tat = len(van_ban_tom_tat.split())
        ty_le_nen = round((1 - so_tu_tom_tat / max(so_tu_goc, 1)) * 100, 1)

        return {
            "summary": van_ban_tom_tat, 
            "latency": thoi_gian_xuly, 
            "compression": max(0.0, ty_le_nen)
        }

    # 2. TÍNH NĂNG PHÂN LOẠI CHUYÊN MỤC & SẮC THÁI
    def process_analysis(self, van_ban):
        text_sach = self._lam_sach_van_ban(van_ban)
        
        try:
            chuyen_muc = classify(text_sach)
            chuoi_chuyen_muc = chuyen_muc[0] if (isinstance(chuyen_muc, list) and len(chuyen_muc) > 0) else str(chuyen_muc)
        except Exception:
            chuoi_chuyen_muc = "Khác"

        try:
            sac_thai = sentiment(text_sach)
            chuoi_sac_thai = str(sac_thai) if sac_thai else "neutral"
        except Exception:
            chuoi_sac_thai = "neutral"

        return {
            "category": chuoi_chuyen_muc, 
            "sentiment": chuoi_sac_thai
        }

    # 3. TÍNH NĂNG TRÍCH XUẤT TỪ KHÓA & THỰC THỂ (NER)
    def process_entities(self, van_ban):
        text_sach = self._lam_sach_van_ban(van_ban)
        
        try:
            nhan_tu_loai = pos_tag(text_sach)
            danh_tu = [
                tu.replace("_", " ").title() for tu, nhan in nhan_tu_loai 
                if nhan.startswith('N') 
                and len(tu) > 1 
                and not tu.isdigit()
                and tu.lower() not in ["ngày", "tháng", "năm", "việc", "khi", "người", "sự", "cuộc"]
            ]
            dem_tu = Counter(danh_tu)
            top_tu_khoa = [phantu[0] for phantu in dem_tu.most_common(7)]
        except Exception:
            top_tu_khoa = []

        try:
            ket_qua_ner = ner(text_sach)
            thuc_the = {"Nơi chốn/Địa danh": set(), "Tên người": set(), "Tổ chức": set()}
            
            for phantu in ket_qua_ner:
                tu, tu_loai, cum_tu, loai_thuc_the = phantu
                tu_sach = tu.replace("_", " ").strip()
                
                if len(tu_sach) <= 2 or tu_sach.lower() in ["độ", "khu vực", "trung tâm", "ông", "bà"]:
                    continue
                    
                if "LOC" in loai_thuc_the: 
                    thuc_the["Nơi chốn/Địa danh"].add(tu_sach)
                elif "PER" in loai_thuc_the: 
                    thuc_the["Tên người"].add(tu_sach)
                elif "ORG" in loai_thuc_the: 
                    thuc_the["Tổ chức"].add(tu_sach)
            
            thuc_the_dinh_dang = {k: list(v) for k, v in thuc_the.items() if len(v) > 0}
        except Exception:
            thuc_the_dinh_dang = {}

        return {
            "keywords": top_tu_khoa, 
            "entities": thuc_the_dinh_dang
        }

    # 4. TRỢ LÝ TRA CỨU HỌC TẬP
    def process_learning_assistant(self, van_ban="", cau_hoi=""):
        thoi_gian_bat_dau = time.time()
        nguon_du_lieu = "Mô hình Trí tuệ Nhân tạo Groq Llama 3.3 70B"
        text_sach = self._lam_sach_van_ban(van_ban)
        cau_hoi_sach = self._lam_sach_van_ban(cau_hoi)

        tra_loi_cau_hoi = ""
        giai_thich_chi_tiet = []

        try:
            if not self.client:
                raise Exception("Chưa tìm thấy GROQ_API_KEY trong cấu hình Secrets")

            prompt_system = (
                "Bạn là một trợ lý giáo dục chuyên nghiệp, thông minh và chính xác. "
                "Nhiệm vụ của bạn là giải thích ngắn gọn, rõ ràng, chính xác theo góc độ học thuật các câu hỏi hoặc bài học của người dùng. "
                "Nếu người dùng cung cấp thêm văn bản bài học, hãy ưu tiên dựa trên nội dung đó để trả lời."
            )
            
            user_content = ""
            if text_sach:
                user_content += f"Văn bản bài học đính kèm:\n{text_sach}\n\n"
            if cau_hoi_sach:
                user_content += f"Câu hỏi của người dùng: {cau_hoi_sach}"
            elif text_sach:
                user_content += "Hãy giải thích các kiến thức cốt lõi nhất trong đoạn văn trên."

            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": user_content}
                ],
                model=self.model_name,
                temperature=0.3
            )
            tra_loi_cau_hoi = response.choices[0].message.content.strip()

        except Exception as e:
            nguon_du_lieu = f"Cảnh báo: {str(e)}"
            tra_loi_cau_hoi = "Chưa tìm thấy API Key. Hãy điền GROQ_API_KEY vào mục Settings -> Secrets trên Streamlit Cloud."

        if tra_loi_cau_hoi and "Chưa tìm thấy API Key" not in tra_loi_cau_hoi:
            kq_thuc_the = self.process_entities(tra_loi_cau_hoi)
            tu_khoa_hoc_tap = kq_thuc_the["keywords"]
            danh_sach_cau = [c.strip() for c in re.split(r'(?<=[.!?])\s+', tra_loi_cau_hoi) if len(c.strip()) > 5]
            
            for tk in tu_khoa_hoc_tap[:4]:
                cau_chua_tu = [c for c in danh_sach_cau if tk.lower() in c.lower()]
                if cau_chua_tu:
                    giai_thich_chi_tiet.append(f"📌 **{tk}**: {cau_chua_tu[0]}")

        thoi_gian_xuly = round(time.time() - thoi_gian_bat_dau, 2)
        
        return {
            "source": nguon_du_lieu,
            "key_concepts": giai_thich_chi_tiet,
            "answer": tra_loi_cau_hoi,
            "latency": thoi_gian_xuly
        }
