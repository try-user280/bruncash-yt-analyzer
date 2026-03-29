import streamlit as st
import google.generativeai as genai
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- CONFIGURATION ---
try:
    YT_API_KEY = st.secrets["YT_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GCP_CREDS = st.secrets["gcp_service_account"]
except Exception as e:
    st.error("Secrets missing! Check Streamlit Advanced Settings.")
    st.stop()

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def save_to_sheets(input_query, ai_response):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        
        row = [str(datetime.now()), input_query[:500], "Advanced Analysis", ai_response[:2000]]
        sheet.append_row(row)
        return True
    except: return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bruncash YouTube Genius", page_icon="🔥")

st.title("🚀 Bruncash YouTube AI Genius")
st.write("YouTube Video Link dalo ya koi bhi sawal pucho!")

# User Input
user_input = st.text_area("Yahan Paste Karein:", placeholder="Link or Question...")

if st.button("Generate Strategy"):
    if user_input:
        v_id_match = re.search(r"(?:v=|\/shorts\/|\/)([0-9A-Za-z_-]{11})", user_input)
        
        with st.spinner("AI Brainstorming..."):
            try:
                if v_id_match:
                    # Video Analysis
                    v_id = v_id_match.group(1)
                    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
                    request = youtube.videos().list(part="snippet,statistics", id=v_id)
                    response = request.execute()
                    
                    if response['items']:
                        item = response['items'][0]
                        title = item['snippet']['title']
                        
                        prompt = f"Analyze this YouTube Video: {title}. Provide SEO Score, 5 Titles, 20 Tags, and Viral Strategy in Hinglish."
                        result = model.generate_content(prompt).text
                        st.subheader(f"📹 Video: {title}")
                    else:
                        st.error("Video not found.")
                        st.stop()
                else:
                    # General YouTube Question
                    prompt = f"Tum ek YouTube Guru ho. Iska detail mein Hinglish mein jawab do: '{user_input}'. Trending topics, channel growth, aur strategy sab cover karo."
                    result = model.generate_content(prompt).text
                    st.subheader("💡 AI Strategy")

                # Display and Save
                st.markdown(result)
                if save_to_sheets(user_input, result):
                    st.success("Data saved to YT_History! ✅")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Kuch toh likho bhai!")
