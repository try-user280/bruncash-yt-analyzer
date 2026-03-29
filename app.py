
import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- SAFE CONFIGURATION (Streamlit Secrets se data uthayega) ---
try:
    # Ye lines keys ko code se bahar rakhti hain taaki API block na ho
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Secrets not found! Please add them in Streamlit Advanced Settings.")
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
        
        # Sheet ka naam 'YT_History' hona chahiye
        sheet = client.open("YT_History").sheet1
        
        row = [
            str(datetime.now()), 
            video_data['title'], 
            video_data['views'], 
            video_data['channel'], 
            ai_report[:1500] 
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Sheet Error: {e}")
        return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bruncash AI Pro", page_icon="🚀")
st.title("💎 Bruncash Viral-AI Analyzer")
st.markdown("YouTube video analyze karein aur data save karein.")

video_url = st.text_input("YouTube Link dalo:")

if st.button("Analyze & Save"):
    if video_url:
        v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", video_url)
        if v_id_match:
            v_id = v_id_match.group(1)
            with st.spinner("AI Analysis chal raha hai..."):
                try:
                    # 1. YouTube Data
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
                        
                        # 2. Gemini AI Analysis (Hinglish)
                        prompt = f"Analyze this video: {video_info['title']}. Views: {video_info['views']}. Tell me why it went viral and suggest 3 better titles and 5 tags in Hinglish."
                        ai_report = model.generate_content(prompt).text
                        
                        st.markdown("### 📊 AI Viral Report")
                        st.write(ai_report)
                        
                        # 3. Save to Google Sheets
                        if save_to_sheets(video_info, ai_report):
                            st.balloons()
                            st.success("Data 'YT_History' mein save ho gaya! ✅")
                    else:
                        st.error("Video nahi mila.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Sahi link dalo bhai!")
