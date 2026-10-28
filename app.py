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
# 🎉 لم نعد بحاجة لمفتاح API! السيستم الآن مجاني ومفتوح
# ==========================================

async def generate_video_logic(idea):
    try:
        # 1. توليد السيناريو من Pollinations AI (مجاني تماماً وبدون مفتاح)
        # نطلب من الموديل إخراج JSON بدقة
        prompt = (
            f"Create a short viral video script about: {idea}. "
            f"Response MUST be a JSON object only. "
            f"Structure: {{'scenes': [{{'visual': 'english image prompt', 'text': 'arabic voiceover'}}]}}. "
            f"Max 3 scenes. No intro, no outro, just JSON."
        )
        
        # استخدام API مجاني لا يتطلب مفتاح
        url = f"https://text.pollinations.ai/{prompt}"
        response = requests.get(url)
        content = response.text
        
        # تنظيف الرد لاستخراج الـ JSON فقط
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # محاولة أخيرة: إذا لم يجد JSON، نصنع سيناريو افتراضي بسيط لضمان عدم توقف البرنامج
            data = {
                "scenes": [
                    {"visual": f"High quality image of {idea}", "text": f"أهلاً بكم في فيديو عن {idea}"},
                    {"visual": f"Cinematic view of {idea}", "text": "شاهدوا هذه التفاصيل المذهلة"},
                    {"visual": f"Closing shot of {idea}", "text": "شكراً للمشاهدة، لا تنسى المتابعة"}
                ]
            }
        
        clips = []
        for i, scene in enumerate(data.get('scenes', [])):
            # أ- توليد الصورة (Pollinations)
            img_url = f"https://image.pollinations.ai/prompt/{scene['visual']}?width=1080&height=1920&nologo=true"
            img_data = requests.get(img_url).content
            img_path = f"img_{i}.jpg"
            with open(img_path, "wb") as f: f.write(img_data)
            
            # ب- توليد الصوت (Edge-TTS)
            audio_path = f"audio_{i}.mp3"
            communicate = edge_tts.Communicate(scene['text'], "ar-EG-ShakirNeural")
            await communicate.save(audio_path)
            
            # ج- دمج
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            clips.append(img_clip)
        
        # دمج المقاطع
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "final_video.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
        
        return output_file

    except Exception as e:
        return f"System Error: {str(e)}"

# --- واجهة Streamlit ---
st.set_page_config(page_title="AI Video Factory", page_icon="🎬")
st.title("🎬 مصنع الفيديوهات السحابي (النسخة المجانية المطلقة)")
st.markdown("✨ هذا النظام يعمل الآن بدون مفاتيح API وبدون قيود!")

idea_input = st.text_input("اكتب فكرة الفيديو هنا", placeholder="مثال: فواكه متكلمة")

if st.button("توليد الفيديو 🚀"):
    if idea_input:
        with st.spinner("⏳ جاري التوليد (بدون مفاتيح)..."):
            video_result = asyncio.run(generate_video_logic(idea_input))
            if video_result.endswith(".mp4"):
                st.success("✅ تم التوليد بنجاح!")
                st.video(video_result)
                with open(video_result, "rb") as file:
                    st.download_button("📥 تحميل الفيديو", data=file, file_name="ai_video.mp4")
            else:
                st.error(video_result)
    else:
        st.warning("⚠️ اكتب فكرة أولاً!")
