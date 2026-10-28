import streamlit as st
import requests
import asyncio
import edge_tts
import os
import json

# --- حل مشكلة استيراد MoviePy لضمان العمل على كل الإصدارات ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        st.error("⚠️ فشل في تحميل مكتبة MoviePy. يرجى التأكد من وجود moviepy في ملف requirements.txt وعمل Reboot للتطبيق.")

# ==========================================
# ⚠️ ضع مفتاح Groq الخاص بك هنا بالأسفل ⚠️
GROQ_API_KEY = "ضع_مفتاحك_هنا"
# ==========================================

async def generate_video_logic(idea):
    try:
        # 1. توليد السيناريو المنظم من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # برومبت دقيق لإجبار الذكاء الاصطناعي على إخراج JSON فقط
        prompt = (
            f"Create a short viral video script for: {idea}. "
            f"Output ONLY a valid JSON object with this structure: "
            f"{{'scenes': [{{'visual': 'detailed english image prompt', 'text': 'short arabic voiceover'}}]}}. "
            f"Make it 3-4 scenes maximum."
        )
        
        response = requests.post(url, headers=headers, json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }).json()
        
        # استخراج البيانات من استجابة Groq
        content = response['choices'][0]['message']['content']
        data = json.loads(content)
        
        clips = []
        
        # معالجة كل مشهد على حدة
        for i, scene in enumerate(data['scenes']):
            # أ- توليد الصورة (مجاني من Pollinations)
            img_url = f"https://image.pollinations.ai/prompt/{scene['visual']}?width=1080&height=1920&nologo=true"
            img_data = requests.get(img_url).content
            img_path = f"img_{i}.jpg"
            with open(img_path, "wb") as f: 
                f.write(img_data)
            
            # ب- توليد الصوت (مجاني من Edge-TTS)
            audio_path = f"audio_{i}.mp3"
            communicate = edge_tts.Communicate(scene['text'], "ar-EG-ShakirNeural")
            await communicate.save(audio_path)
            
            # ج- دمج الصورة والصوت في مقطع واحد
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            clips.append(img_clip)
        
        # دمج جميع المقاطع في فيديو واحد نهائي
        final_video = concatenate_vide
