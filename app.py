import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- CONFIGURATION (Streamlit Secrets se data fetch karega) ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Secrets not found! Please add them in Streamlit Settings.")
    st.stop()

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def save_to_sheets(video_data, ai_report):
    """Google Sheet 'YT_History' mein data save karne ke liye"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        
        # Sheet ka naam wahi hona chahiye jo tumne banaya hai
        sheet = client.open("YT_History").sheet1
        
        # Nayi row taiyar karein
        row = [
            str(datetime.now()), 
            video_data['title'], 
            video_data['views'], 
            video_data['channel'], 
            ai_report[:1500] # Report ko thoda limit mein rakha hai
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Sheet Error: {e}")
        return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bruncash AI Pro", page_icon="🚀")
st.title("💎 Bruncash Viral-AI Analyzer")
st.markdown("Apne YouTube videos ka analysis karein aur data permanently save karein.")

# Input Field
video_url = st.text_input("YouTube Video ya Shorts ka link dalo:")

if st.button("Analyze & Save"):
    if video_url:
        # Video ID nikalne ka logic
        v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", video_url)
        if v_id_match:
            v_id = v_id_match.group(1)
            
            with st.spinner("AI Magic dikha raha hai..."):
                try:
                    # 1. YouTube se Data Fetch
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        video_info = {
                            "title": item['snippet']['title'],
                            "views": item['statistics'].get('viewCount', '0'),
                            "channel": item['snippet']['channelTitle']
                        }
                        
                        st.success(f"Video Mil Gaya: {video_info['title']}")
                        
                        # 2. Gemini AI se Analysis
                        prompt = f"""
                        Tum ek YouTube Growth Expert ho. Is video ka deep analysis karo:
                        Title: {video_info['title']}
                        Views: {video_info['views']}
                        Channel: {video_info['channel']}
                        
                        Mujhe Hinglish mein batao:
                        1. Ye video viral kyun hua?
                        2. Iska SEO score kya hai?
                        3. 3 Viral Title suggestions.
                        4. 5 best tags.
                        """
                        ai_report = model.generate_content(prompt).text
                        
                        # Report Display
                        st.markdown("### 📊 AI Viral Report")
                        st.write(ai_report)
                        
                        # 3. Google Sheet mein Save
                        if save_to_sheets(video_info, ai_report):
                            st.balloons()
                            st.success("Data 'YT_History' sheet mein save ho gaya! ✅")
                    else:
                        st.error("Video data nahi mila. Link check karein.")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Bhai, sahi YouTube link dalo!")
    else:
        st.info("Pehle link toh dalo!")

st.sidebar.markdown("---")
st.sidebar.write("Developed by Brun 🚀")