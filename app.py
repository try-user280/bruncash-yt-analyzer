import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SECRETS SETUP ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("❌ Secrets Missing! Please check Streamlit Advanced Settings.")
    st.stop()

# --- 2. GEMINI AI SETUP (Latest Model) ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. GOOGLE SHEETS SETUP ---
def save_to_sheets(query, response_text):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        row = [str(datetime.now()), str(query)[:500], "Bruncash 2025 Final", str(response_text)[:2500]]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.sidebar.error(f"Sheet Error: {e}")
        return False

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Bruncash 2025 AI Master", page_icon="🔥", layout="wide")

st.title("💎 Bruncash 2025 YouTube AI Master")
st.markdown("YouTube Link dalo ya koi bhi sawal pucho. Ye All-in-One AI sabka jawab dega!")

# User Input Box
user_input = st.text_area("Yahan Paste Karein (Link, Channel Name, ya Sawal):", 
                          placeholder="Example: https://youtube.com/shorts/... ya 'Aajjubhai ke subs?'", 
                          height=150)

# Main Button
if st.button("🚀 Analyze & Generate Strategy"):
    if not user_input.strip():
        st.warning("⚠️ Bhai, pehle box mein kuch likho ya link dalo!")
    else:
        with st.spinner("⏳ AI Brainstorming kar raha hai..."):
            try:
                # YouTube Link Check
                v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
                
                if v_id_match:
                    # VIDEO ANALYSIS MODE
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        views = item['statistics'].get('viewCount', '0')
                        
                        prompt = f"Tum ek YouTube SEO Expert ho. Is video ka full analysis karo: Title: {title}, Views: {views}. Hinglish mein report do: 1. Viral Factor, 2. SEO Score, 3. 5 Viral Titles, 4. 20 Rankable Tags."
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video Analysis: {title}")
                    else:
                        st.error("Video data nahi mila! Shayad link galat hai.")
                        st.stop()
                else:
                    # GENERAL AI MODE (Questions, Channel Research, Trends)
                    prompt = f"Tum ek YouTube Strategy Guru ho. User ka sawal hai: '{user_input}'. Isko detail mein Hinglish mein samjhao. Channel growth, subscriber details, aur trending topics par focus karo."
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy & Insights")

                # Results Display
                st.markdown(result)
                
                # Save to Sheets
                if save_to_sheets(user_input, result):
                    st.success("✅ Analysis successfully saved to 'YT_History' Sheet!")
                    
            except Exception as e:
                st.error(f"❌ System Error: {e}")

st.sidebar.info("Developed by Brun [Class 9] 🚀")
