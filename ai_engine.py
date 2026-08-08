# -*- coding: utf-8 -*-
import sys
import os
import io
import base64
import pandas as pd
import docx
from pypdf import PdfReader
from groq import Groq
import streamlit as st

# Ép hệ thống dùng chuẩn UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AIEngine:
    def __init__(self):
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
            
        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "llama-3.2-11b-vision-preview"

    # 1. Đọc sạch 100% file PDF (Dành cho sách giáo khoa / tài liệu dài)
    def extract_pdf(self, file_bytes):
        try:
            reader = PdfReader(file_bytes)
            text_pages = []
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt and txt.strip():
                    text_pages.append(f"[Trang {i+1}]: {txt.strip()}")
            full_text = "\n".join(text_pages)
            return full_text if full_text.strip() else "Không thể trích xuất được chữ từ PDF (Có thể file là dạng ảnh quét)."
        except Exception as e:
            return f"Lỗi khi đọc file PDF: {str(e)}"

    # 2. Đọc file Word (.docx)
    def extract_word(self, file_bytes):
        try:
            doc = docx.Document(file_bytes)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            return f"Lỗi khi đọc file Word: {str(e)}"

    # 3. Đọc file Excel (.xlsx, .xls)
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

    # 4. Phân tích Hình Ảnh
    def analyze_image(self, file_bytes, prompt="Hãy đọc và trích xuất toàn bộ văn bản/nội dung có trong hình ảnh này."):
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
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi xử lý hình ảnh: {str(e)}"

    # 5. Hàm Chat nhớ toàn bộ ngữ cảnh giống Gemini/ChatGPT
    def chat_with_memory(self, messages_history):
        if not self.client:
            return "Chưa tìm thấy API Key. Hãy điền GROQ_API_KEY vào mục Settings -> Secrets trên Streamlit Cloud."

        try:
            system_instruction = {
                "role": "system",
                "content": (
                    "Bạn là một Trợ lý AI giáo dục thông minh và chu đáo. "
                    "Hãy luôn ghi nhớ toàn bộ nội dung các tệp đính kèm (PDF, Word, Excel, Ảnh) "
                    "và lịch sử các câu hỏi trước đó của người dùng để trả lời chính xác, đầy đủ nhất."
                )
            }
            
            # Đảm bảo định dạng chuẩn gửi lên Groq API
            api_messages = [system_instruction]
            for m in messages_history:
                api_messages.append({"role": m["role"], "content": m["content"]})

            response = self.client.chat.completions.create(
                messages=api_messages,
                model=self.text_model,
                temperature=0.3,
                max_tokens=3000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi kết nối AI: {str(e)}"
