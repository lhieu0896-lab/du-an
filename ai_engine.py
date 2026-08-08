# -*- coding: utf-8 -*-
import sys
import os
import io
import base64
import pandas as pd
import docx
import bcrypt
from pypdf import PdfReader
from groq import Groq
from supabase import create_client, Client
from duckduckgo_search import DDGS
import streamlit as st

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AIEngine:
    def __init__(self):
        # 1. Khởi tạo Groq API Client
        self.api_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY", "")

        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

        # 2. Khởi tạo Supabase Database Client
        self.supabase: Client = None
        self.db_status = "CHƯA_KẾT_NỐI"
        try:
            sb_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
            sb_key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY", "")

            if sb_url and sb_key:
                self.supabase = create_client(sb_url, sb_key)
                self.db_status = "ĐÃ_KẾT_NỐI"
        except Exception as e:
            self.db_status = f"LỖI: {str(e)}"

        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "llama-3.2-11b-vision-preview"

    # --- HỆ THỐNG ĐĂNG KÝ & ĐĂNG NHẬP BẢO MẬT ---
    def register_user(self, full_name, username, password):
        """Tạo tài khoản người dùng mới và mã hóa mật khẩu"""
        if not self.supabase:
            return False, "Chưa kết nối Database Supabase!"
        try:
            username_clean = username.strip().lower()
            res = self.supabase.table("users").select("*").eq("username", username_clean).execute()
            if res.data:
                return False, "Tên tài khoản này đã tồn tại trên hệ thống!"
            
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            self.supabase.table("users").insert({
                "full_name": full_name.strip(),
                "username": username_clean,
                "password_hash": hashed_pw
            }).execute()
            
            return True, "Đăng ký tài khoản thành công!"
        except Exception as e:
            return False, f"Lỗi đăng ký: {str(e)}"

    def authenticate_user(self, username, password):
        """Xác thực thông tin đăng nhập của người dùng"""
        if not self.supabase:
            return None, "Chưa kết nối Database Supabase!"
        try:
            username_clean = username.strip().lower()
            res = self.supabase.table("users").select("*").eq("username", username_clean).execute()
            if not res.data:
                return None, "Tên tài khoản hoặc mật khẩu không chính xác!"
            
            user_info = res.data[0]
            stored_hash = user_info["password_hash"].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return user_info, "Đăng nhập thành công!"
            else:
                return None, "Tên tài khoản hoặc mật khẩu không chính xác!"
        except Exception as e:
            return None, f"Lỗi đăng nhập: {str(e)}"

    # --- TRA CỨU WEB REAL-TIME ---
    def search_web(self, query, max_results=5):
        try:
            results = []
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, region="vn-vi", max_results=max_results))
                if not ddg_results:
                    ddg_results = list(ddgs.text(query, max_results=max_results))
                
                for r in ddg_results:
                    title = r.get('title', '')
                    href = r.get('href', '')
                    body = r.get('body', '')
                    if body:
                        results.append(f"📌 **{title}**\nNguồn: {href}\nNội dung: {body}\n")
                        
            return "\n".join(results) if results else "CHƯA_CÓ_KẾT_QUẢ"
        except Exception as e:
            print(f"Lỗi tìm kiếm web: {e}")
            return f"Lỗi truy cập kết quả tìm kiếm Web: {str(e)}"

    # --- TỰ ĐỘNG ĐẶT TÊN CHAT ---
    def generate_chat_title(self, first_user_message):
        if not self.client:
            return "Cuộc trò chuyện mới"
        try:
            prompt = (
                f"Hãy tạo một tiêu đề ngắn gọn (từ 3 đến 5 từ) bằng tiếng Việt cho cuộc trò chuyện có câu hỏi đầu tiên là: '{first_user_message}'. "
                "Chỉ trả về duy nhất chuỗi tiêu đề, không ghi thêm dấu ngoặc kép hay từ thừa."
            )
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )
            title = response.choices[0].message.content.strip().replace('"', '')
            return title if title else "Cuộc trò chuyện mới"
        except Exception:
            return "Cuộc trò chuyện mới"

    # --- TRÍCH XUẤT PHẦN VĂN BẢN TÀI LIỆU DÀI ---
    def retrieve_relevant_chunks(self, full_text, query, chunk_size=1500, top_k=3):
        if len(full_text) <= chunk_size * 2:
            return full_text

        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size - 200)]
        query_words = set(query.lower().split())
        scored_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if len(word) > 2 and word in chunk_lower)
            scored_chunks.append((score, chunk))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        selected_chunks = [item[1] for item in scored_chunks[:top_k]]
        return "\n\n...[Đoạn trích xuất từ tài liệu]...\n\n".join(selected_chunks)

    # --- XUẤT ĐOẠN CHAT RA FILE WORD ---
    def export_chat_to_word(self, messages, chat_title):
        doc = docx.Document()
        doc.add_heading(f"BÁO CÁO TRÒ CHUYỆN: {chat_title}", level=1)
        doc.add_paragraph("Được trích xuất từ Hệ thống NEXUS AI\n-----------------------------------")
        
        for m in messages:
            role_name = "NGƯỜI DÙNG" if m["role"] == "user" else "TRỢ LÝ AI"
            content_text = m.get("display_content", m["content"])
            
            p = doc.add_paragraph()
            p.add_run(f"[{role_name}]:\n").bold = True
            p.add_run(f"{content_text}\n")
            
        target_stream = io.BytesIO()
        doc.save(target_stream)
        target_stream.seek(0)
        return target_stream

    # --- XỬ LÝ SUPABASE DATABASE RIÊNG BIỆT CHO TỪNG USER_ID ---
    def load_user_chats(self, user_id):
        if not self.supabase:
            return {}
        try:
            res = self.supabase.table("chats").select("*").eq("user_id", str(user_id)).order("created_at", desc=False).execute()
            chats = {}
            for row in res.data:
                chat_id = row["id"]
                title = row["title"]
                msg_res = self.supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
                chats[title] = {
                    "id": chat_id,
                    "messages": [
                        {
                            "role": m["role"],
                            "content": m["content"],
                            "display_content": m.get("display_content") or m["content"]
                        } for m in msg_res.data
                    ]
                }
            return chats
        except Exception as e:
            print(f"Lỗi load DB: {e}")
            return {}

    def save_chat_node(self, chat_id, title, user_id):
        if self.supabase:
            try:
                self.supabase.table("chats").upsert({"id": chat_id, "title": title, "user_id": str(user_id)}).execute()
            except Exception as e:
                print(f"Lỗi save chat node: {e}")

    def save_message(self, chat_id, role, content, display_content=""):
        if self.supabase:
            try:
                self.supabase.table("messages").insert({
                    "chat_id": chat_id,
                    "role": role,
                    "content": content,
                    "display_content": display_content
                }).execute()
            except Exception as e:
                print(f"Lỗi save message: {e}")

    def delete_chat(self, chat_id):
        if self.supabase:
            try:
                self.supabase.table("chats").delete().eq("id", chat_id).execute()
            except Exception as e:
                print(f"Lỗi delete chat: {e}")

    def update_chat_title(self, chat_id, new_title):
        if self.supabase:
            try:
                self.supabase.table("chats").update({"title": new_title}).eq("id", chat_id).execute()
            except Exception as e:
                print(f"Lỗi update title: {e}")

    # --- ĐỌC TỆP ĐA ĐỊNH DẠNG ---
    def extract_pdf(self, file_bytes):
        try:
            reader = PdfReader(file_bytes)
            text_pages = []
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt and txt.strip():
                    text_pages.append(f"[Trang {i+1}]: {txt.strip()}")
            full_text = "\n".join(text_pages)
            return full_text if full_text.strip() else "PDF_IS_SCANNED_IMAGE"
        except Exception as e:
            return f"Lỗi khi đọc file PDF: {str(e)}"

    def extract_word(self, file_bytes):
        try:
            doc = docx.Document(file_bytes)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            return f"Lỗi khi đọc file Word: {str(e)}"

    def extract_excel(self, file_bytes):
        try:
            df_dict = pd.read_excel(file_bytes, sheet_name=None)
            extracted_text = []
            for sheet_name, df in df_dict.items():
                extracted_text.append(f"--- Sheet: {sheet_name} ---")
                extracted_text.append(df.to_markdown(index=False))
            return "\n".join(extracted_text)
        except Exception as e:
            return f"Lỗi khi đọc file Excel: {str(e)}"

    def analyze_image(self, file_bytes, prompt="Hãy đọc và trích xuất toàn bộ chữ viết có trong hình này."):
        if not self.client:
            return "Chưa cấu hình GROQ_API_KEY."
        try:
            base64_image = base64.b64encode(file_bytes.getvalue()).decode('utf-8')
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi Vision AI: {str(e)}"

    # --- CHAT STREAMING KỶ LUẬT ĐỘ CHÍNH XÁC CAO ---
    def chat_stream(self, clean_messages_history, web_search_context=""):
        if not self.client:
            yield "Chưa tìm thấy API Key Groq."
            return
        try:
            system_instruction_text = (
                "Bạn là Trợ lý AI giáo dục thông minh và hữu ích của Nhóm NEXUS. "
                "TUÂN THỦ NGUYÊN TẮC VÀNG: Trả lời chính xác, khoa học, logic bằng tiếng Việt. "
                "Nếu gặp câu hỏi không đủ thông tin hoặc nằm ngoài tri thức chắc chắn, hãy thẳng thắn trả lời 'Tôi không đủ thông tin chắc chắn về vấn đề này' chứ tuyệt đối không được tự đoán. "
                "Sử dụng Markdown rõ ràng và LaTeX ($...$) cho công thức toán/hóa."
            )
            
            if web_search_context and web_search_context != "CHƯA_CÓ_KẾT_QUẢ":
                system_instruction_text += (
                    f"\n\n[DỮ LIỆU TRA CỨU MỚI NHẤT TỪ WEB REAL-TIME]:\n{web_search_context}\n\n"
                    "Hãy tổng hợp thông tin từ nguồn tra cứu trên để trả lời trực tiếp cho người dùng."
                )

            system_instruction = {"role": "system", "content": system_instruction_text}
            api_messages = [system_instruction] + clean_messages_history
            
            response_stream = self.client.chat.completions.create(
                messages=api_messages,
                model=self.text_model,
                temperature=0.0,
                max_tokens=4000,
                stream=True
            )
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Lỗi kết nối AI: {str(e)}"
