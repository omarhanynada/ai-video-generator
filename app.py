import streamlit as st
import requests
import asyncio
import edge_tts
import os
import json
import re

# --- حل مشكلة استيراد MoviePy ---
try:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    except ImportError:
        st.error("⚠️ فشل في تحميل مكتبة MoviePy.")

# ==========================================
# ✅ مفتاحك مدمج هنا
GROQ_API_KEY = "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"
# ==========================================

# الموديلات الأكثر استقراراً حالياً
MODELS = ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "llama3-70b-8192"]

async def generate_video_logic(idea):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # برومبت بسيط جداً ومباشر
        prompt = f"Write a video script about {idea}. Format: JSON only. Structure: {{'scenes': [{{'visual': 'image prompt', 'text': 'arabic voiceover'}}]}}. Max 3 scenes."
        
        response_json = None
        for model in MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
                res = requests.post(url, headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    response_json = res.json()
                    break
            except:
                continue

        if not response_json:
            return "API Error: Groq refused the request. Please check if your API key is still active."
            
        content = response_json['choices'][0]['message']['content']
        
        # تنظيف الـ JSON بدقة
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            return "AI Error: The response was not in JSON format."
        
        clips = []
        for i, scene in enumerate(data.get('scenes', [])):
            # أ- صورة
            img_url = f"https://image.pollinations.ai/prompt/{scene['visual']}?width=1080&height=1920&nologo=true"
            img_data = requests.get(img_url).content
            img_path = f"img_{i}.jpg"
            with open(img_path, "wb") as f: f.write(img_data)
            
            # ب- صوت
            audio_path = f"audio_{i}.mp3"
            communicate = edge_tts.Communicate(scene['text'], "ar-EG-ShakirNeural")
            await communicate.save(audio_path)
            
            # ج- دمج
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            clips.append(img_clip)
        
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "final_video.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        return output_file

    except Exception as e:
        return f"System Error: {str(e)}"

# --- واجهة Streamlit ---
st.set_page_config(page_title="AI Video Factory", page_icon="🎬")
st.title("🎬 مصنع الفيديوهات السحابي المجاني")

idea_input = st.text_input("اكتب فكرة الفيديو هنا", placeholder="مثال: فواكه متكلمة")

if st.button("توليد الفيديو 🚀"):
    if idea_input:
        with st.spinner("⏳ جاري التوليد..."):
            video_result = asyncio.run(generate_video_logic(idea_input))
            if video_result.endswith(".mp4"):
                st.success("✅ تم التوليد!")
                st.video(video_result)
                with open(video_result, "rb") as file:
                    st.download_button("📥 تحميل الفيديو", data=file, file_name="ai_video.mp4")
            else:
                st.error(video_result)
    else:
        st.warning("⚠️ اكتب فكرة أولاً!")
