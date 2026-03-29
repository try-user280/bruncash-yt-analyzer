import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP & SECRETS ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("❌ Secrets Missing: Streamlit Advanced Settings mein keys check karein!")
    st.stop()

# Model setup (Updated Library ke saath ye 100% chalega)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. GOOGLE SHEETS SAVING ---
def save_to_sheets(query, response_text):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        row = [str(datetime.now()), str(query)[:500], "Bruncash 2025 Output", str(response_text)[:2500]]
        sheet.append_row(row)
        return True
    except:
        return False

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="Bruncash 2025", page_icon="🔥", layout="wide")
st.title("💎 Bruncash 2025 YouTube AI Master")
st.markdown("Video Link dalo ya YouTube ka koi bhi sawal pucho!")

user_input = st.text_area("Yahan Paste Karein (Link ya Sawal):", placeholder="Example: Aajjubhai ki growth strategy?")

if st.button("🚀 Analyze & Generate Strategy"):
    if not user_input.strip():
        st.warning("⚠️ Bhai, pehle box mein kuch likho!")
    else:
        with st.spinner("⏳ AI Brainstorming kar raha hai..."):
            try:
                v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
                
                if v_id_match:
                    # VIDEO MODE
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        views = item['statistics'].get('viewCount', '0')
                        
                        prompt = f"YouTube SEO Expert ban kar is video ka post-mortem karo: Title: {title}, Views: {views}. Hinglish mein report do: 1. Viral Factor, 2. SEO Score, 3. 5 Viral Titles, 4. 20 Rankable Tags."
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video Analysis: {title}")
                    else:
                        st.error("Video data nahi mila! Shayad link galat hai.")
                        st.stop()
                else:
                    # GENERAL AI MODE
                    prompt = f"Tum ek YouTube Strategy Guru ho. User ka sawal hai: '{user_input}'. Isko detail mein Hinglish mein samjhao. Channel ya trending topics par focus karo."
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy & Insights")

                st.markdown(result)
                if save_to_sheets(user_input, result):
                    st.success("✅ Analysis successfully saved to 'YT_History' Sheet!")
                    
            except Exception as e:
                st.error(f"❌ System Error: {e}")
