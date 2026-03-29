import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- CONFIGURATION (Safe & Stable) ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Secrets missing! Check Streamlit Settings.")
    st.stop()

# Gemini AI Setup - Version fix to avoid 404
genai.configure(api_key=GEMINI_API_KEY)
# 'gemini-pro' sabse stable model hai jo har jagah chalta hai
model = genai.GenerativeModel('gemini-pro')

def save_to_sheets(input_query, ai_response):
    """Google Sheet storage logic"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        
        row = [str(datetime.now()), str(input_query)[:500], "Strategy/SEO Analysis", str(ai_response)[:2500]]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.sidebar.error(f"Sheet Error: {e}")
        return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bruncash YouTube Genius", page_icon="🔥")

st.title("🚀 Bruncash YouTube AI Genius")
st.markdown("YouTube ke bare mein kuch bhi puche - Strategy, SEO ya Trending Topics!")

# User Input Box
user_input = st.text_area("Yahan YouTube Link dalo ya sawal pucho:", placeholder="Example: Viral topics for 2026? or paste a video link...")

if st.button("Generate Strategy"):
    if user_input:
        v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
        
        with st.spinner("AI Magic is working..."):
            try:
                if v_id_match:
                    # MODE: Video Analysis
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        prompt = f"Detailed SEO Analysis for this YouTube Video: {title}. Give me SEO Score, 5 Titles, and Viral Strategy in Hinglish."
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video: {title}")
                    else:
                        st.error("Video data nahi mila.")
                        st.stop()
                else:
                    # MODE: General Question
                    prompt = f"Tum ek YouTube Expert ho. Iska detail mein professional Hinglish mein jawab do: '{user_input}'. Analysis poora deep hona chahiye."
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy Insights")

                # Display Result
                st.markdown(result)
                
                # Save to Sheets
                if save_to_sheets(user_input, result):
                    st.success("Data permanently saved in 'YT_History' Sheet! ✅")
                else:
                    st.warning("Analysis complete, par Sheet mein save nahi ho paya. Permissions check karein.")

            except Exception as e:
                st.error(f"AI Error: {e}")
    else:
        st.warning("Bhai, kuch toh likho!")

st.sidebar.write("Developed by Brun 🚀")
