import streamlit as st
import requests
import asyncio
import edge_tts
import os
import json

# --- حل مشكلة استيراد MoviePy ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        st.error("⚠️ فشل في تحميل مكتبة MoviePy.")

# ==========================================
# ✅ تم وضع مفتاحك الخاص هنا بنجاح
GROQ_API_KEY = "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"
# ==========================================

async def generate_video_logic(idea):
    try:
        # 1. توليد السيناريو من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        prompt = (
            f"Create a short viral video script for: {idea}. "
            f"Output ONLY a valid JSON object with this structure: "
            f"{{'scenes': [{{'visual': 'detailed english image prompt', 'text': 'short arabic voiceover'}}]}}. "
            f"Make it 3 scenes maximum."
        )
        
        response_raw = requests.post(url, headers=headers, json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        })
        
        if response_raw.status_code != 200:
            return f"API Error ({response_raw.status_code}): {response_raw.text}"
            
        response = response_raw.json()
        
        if 'choices' not in response:
            return f"Unexpected API Response
