# -*- coding: utf-8 -*-
import sys
import os
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
            
        self.model_name = "llama-3.3-70b-versatile"

    def chat_with_memory(self, messages_history):
        """
        Hàm gửi toàn bộ lịch sử trò chuyện lên Groq để AI có trí nhớ ngữ cảnh
        """
        if not self.client:
            return "Chưa tìm thấy API Key. Hãy điền GROQ_API_KEY vào mục Settings -> Secrets trên Streamlit Cloud."

        try:
            # Prompt định hình tính cách cho AI
            system_instruction = {
                "role": "system",
                "content": (
                    "Bạn là một Trợ lý AI thông minh, thân thiện, trả lời chính xác và tự nhiên bằng tiếng Việt. "
                    "Hãy luôn ghi nhớ ngữ cảnh và các thông tin người dùng đã chia sẻ trong suốt cuộc trò chuyện này."
                )
            }
            
            # Gộp prompt hệ thống + toàn bộ lịch sử chat
            full_messages = [system_instruction] + messages_history

            response = self.client.chat.completions.create(
                messages=full_messages,
                model=self.model_name,
                temperature=0.6,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Lỗi kết nối AI: {str(e)}"
