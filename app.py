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
# ✅ مفتاحك الخاص مدمج هنا
GROQ_API_KEY = "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"
# ==========================================

async def generate_video_logic(idea):
    try:
        # 1. توليد السيناريو من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # برومبت قوي لإجبار الموديل على إخراج JSON بدون استخدام response_format
        prompt = (
            f"You are a professional content creator. Create a short viral video script about: {idea}. "
            f"Return the response ONLY as a valid JSON object. Do not write any intro or outro. "
            f"The JSON structure must be: "
            f"{{'scenes': [{{'visual': 'detailed english image prompt', 'text': 'short arabic voiceover'}}]}}. "
            f"Keep it to 3 scenes maximum."
        )
        
        response_raw = requests.post(url, headers=headers, json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        })
        
        if response_raw.status_code != 200:
            return "API Error: " + str(response_raw.status_code) + " - " + response_raw.text
            
        response = response_raw.json()
        content = response['choices'][0]['message']['content']
        
        # تنظيف الرد من أي علامات Markdown (مثل ```json ... ```)
        json_str = re.sub(r'```json|```', '', content).strip()
        data = json.loads(json_str)
        
        clips = []
        
        for i, scene in enumerate(data['scenes']):
            # أ- توليد الصورة
            img_url = "https://image.pollinations.ai/prompt/" + scene['visual'] + "?width=1080&height=1920&nologo=true"
            img_data = requests.get(img_url).content
            img_path = "img_" + str(i) + ".jpg"
            with open(img_path, "wb") as f: 
                f.write(img_data)
            
            # ب- توليد الصوت
            audio_path = "audio_" + str(i) + ".mp3"
            communicate = edge_tts.Communicate(scene['text'], "ar-EG-ShakirNeural")
            await communicate.save(audio_path)
            
            # ج- دمج الصورة والصوت
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            clips.append(img_clip)
        
        # دمج المقاطع
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "final_video.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        return output_file

    except Exception as e:
        return "System Error: " + str(e)

# --- واجهة Streamlit ---
st.set_page_config(page_title="AI Video Factory", page_icon="🎬")
st.title("🎬 مصنع الفيديوهات السحابي المجاني")

idea_input = st.text_input("اكتب فكرة الفيديو هنا", placeholder="مثال: فواكه متكلمة")

if st.button("توليد الفيديو 🚀"):
    if idea_input:
        with st.spinner("⏳ جاري التفكير وتوليد الفيديو..."):
            video_result = asyncio.run(generate_video_logic(idea_input))
            if video_result.endswith(".mp4"):
                st.success("✅ تم التوليد بنجاح!")
                st.video(video_result)
                with open(video_result, "rb") as file:
                    st.download_button("📥 تحميل الفيديو", data=file, file_name="ai_video.mp4")
            else:
                st.error("حدث خطأ: " + video_result)
    else:
        st.warning("⚠️ اكتب فكرة أولاً!")
