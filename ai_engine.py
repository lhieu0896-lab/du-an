# -*- coding: utf-8 -*-
import sys
import os
import io
import base64
import pandas as pd
import docx
from pypdf import PdfReader
from groq import Groq
from supabase import create_client, Client
import streamlit as st

# Ép hệ thống dùng chuẩn UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AIEngine:
    def __init__(self):
        # 1. Khởi tạo Groq API
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
        try:
            sb_url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
            sb_key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
            if sb_url and sb_key:
                self.supabase = create_client(sb_url, sb_key)
        except Exception as e:
            print(f"Chưa cấu hình Supabase: {e}")

        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "llama-3.2-11b-vision-preview"

    # --- CÁC HÀM XỬ LÝ DATABASE SUPABASE ---
    def load_all_chats(self):
        """Lấy danh sách các cuộc trò chuyện từ Database"""
        if not self.supabase:
            return {}
        try:
            res = self.supabase.table("chats").select("*").order("created_at", desc=False).execute()
            chats = {}
            for row in res.data:
                chat_id = row["id"]
                title = row["title"]
                # Lấy tin nhắn của từng chat
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

    def save_chat_node(self, chat_id, title):
        """Tạo đoạn chat mới vào DB"""
        if self.supabase:
            try:
                self.supabase.table("chats").upsert({"id": chat_id, "title": title}).execute()
            except Exception as e:
                print(f"Lỗi save chat node: {e}")

    def save_message(self, chat_id, role, content, display_content=""):
        """Lưu tin nhắn mới vào DB"""
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
        """Xóa đoạn chat trong DB"""
        if self.supabase:
            try:
                self.supabase.table("chats").delete().eq("id", chat_id).execute()
            except Exception as e:
                print(f"Lỗi delete chat: {e}")

    def update_chat_title(self, chat_id, new_title):
        """Đổi tên đoạn chat trong DB"""
        if self.supabase:
            try:
                self.supabase.table("chats").update({"title": new_title}).eq("id", chat_id).execute()
            except Exception as e:
                print(f"Lỗi update title: {e}")

    # --- CÁC HÀM XỬ LÝ TỆP & AI ---
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

    def chat_stream(self, clean_messages_history):
        if not self.client:
            yield "Chưa tìm thấy API Key."
            return
        try:
            system_instruction = {
                "role": "system",
                "content": (
                    "Bạn là Trợ lý AI giáo dục thông minh như Gemini. Trả lời chính xác, khoa học bằng tiếng Việt. "
                    "Định dạng Markdown đẹp mắt, dùng LaTeX ($...$) cho công thức toán/hóa. "
                    "Hãy ghi nhớ toàn bộ nội dung tệp đính kèm và lịch sử chat."
                )
            }
            api_messages = [system_instruction] + clean_messages_history
            response_stream = self.client.chat.completions.create(
                messages=api_messages,
                model=self.text_model,
                temperature=0.4,
                max_tokens=4000,
                stream=True
            )
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Lỗi kết nối AI: {str(e)}"
