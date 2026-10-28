import streamlit as st
import requests
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import os
import json

# ضع مفتاح Groq الخاص بك هنا
GROQ_API_KEY = "ضع_مفتاحك_هنا"

async def generate_video_logic(idea):
    try:
        # 1. توليد السيناريو
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        prompt = f"Create a short viral video script for: {idea}. Output ONLY a JSON object: {{'scenes': [{{'visual': 'detailed english image prompt', 'text': 'short arabic voiceover'}}]}}"
        
        response = requests.post(url, headers=headers, json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }).json()
        
        data = json.loads(response['choices'][0]['message']['content'])
        
        clips = []
        for i, scene in enumerate(data['scenes']):
            # 2. توليد الصورة
            img_url = f"https://image.pollinations.ai/prompt/{scene['visual']}?width=1080&height=1920&nologo=true"
            img_data = requests.get(img_url).content
            img_path = f"img_{i}.jpg"
            with open(img_path, "wb") as f: f.write(img_data)
            
            # 3. توليد الصوت
            audio_path = f"audio_{i}.mp3"
            communicate = edge_tts.Communicate(scene['text'], "ar-EG-ShakirNeural")
            await communicate.save(audio_path)
            
            # 4. دمج
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).set_audio(audio_clip)
            clips.append(img_clip)
        
        final_video = concatenate_videoclips(clips, method="compose")
        output_file = "final_video.mp4"
        final_video.write_videofile(output_file, fps=24, codec="libx264")
        return output_file
    except Exception as e:
        return str(e)

# واجهة Streamlit
st.title("🎬 مصنع الفيديوهات السحابي")
idea = st.text_input("اكتب فكرة الفيديو هنا", placeholder="مثال: قطة في الفضاء")

if st.button("توليد الفيديو 🚀"):
    if idea:
        with st.spinner("جاري العمل... انتظر قليلاً"):
            video_path = asyncio.run(generate_video_logic(idea))
            if video_path.endswith(".mp4"):
                st.video(video_path)
                with open(video_path, "rb") as file:
                    st.download_button("تحميل الفيديو", data=file, file_name="ai_video.mp4")
            else:
                st.error(f"حدث خطأ: {video_path}")
    else:
        st.warning("من فضلك اكتب فكرة أولاً!")
