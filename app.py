import streamlit as st
import requests  # Ye direct call karega, koi library error nahi!
import json
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

# --- 2. DIRECT GEMINI API BYPASS ---
def ask_gemini(prompt):
    """Google ki library hatakar direct server se baat karne ka function"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts":[{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"API Error: Check your Gemini Key. Details: {response.text}"

# --- 3. GOOGLE SHEETS SETUP ---
def save_to_sheets(query, response_text):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(GCP_CREDS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("YT_History").sheet1
        row = [str(datetime.now()), str(query)[:500], "Bruncash AI (Direct API)", str(response_text)[:2500]]
        sheet.append_row(row)
        return True
    except:
        return False

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="Bruncash 2025 AI Master", page_icon="🔥", layout="wide")
st.title("💎 Bruncash 2025 YouTube AI Master")
st.markdown("Video Link dalo ya YouTube ka koi bhi sawal pucho!")

user_input = st.text_area("Yahan Paste Karein (Link ya Sawal):", placeholder="Example: Aajjubhai ki growth strategy?")

if st.button("🚀 Analyze & Generate Strategy"):
    if not user_input.strip():
        st.warning("⚠️ Bhai, pehle upar box mein kuch likho!")
    else:
        with st.spinner("⏳ AI Brainstorming kar raha hai..."):
            try:
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
                        
                        prompt = f"YouTube SEO Expert ban kar is video ka post-mortem karo: Title: {title}, Views: {views}. Hinglish mein report do: 1. Viral Factor, 2. SEO Score, 3. 5 Viral Titles, 4. 20 Rankable Tags."
                        result = ask_gemini(prompt)  # Naya bypass function
                        st.subheader(f"📹 Video Analysis: {title}")
                    else:
                        st.error("Video data nahi mila! Shayad link galat hai.")
                        st.stop()
                else:
                    # GENERAL AI MODE
                    prompt = f"Tum ek YouTube Strategy Guru ho. User ka sawal hai: '{user_input}'. Isko detail mein Hinglish mein samjhao. Channel ya trending topics par focus karo."
                    result = ask_gemini(prompt)  # Naya bypass function
                    st.subheader("💡 AI Strategy & Insights")

                st.markdown(result)
                if save_to_sheets(user_input, result):
                    st.success("✅ Analysis successfully saved to 'YT_History' Sheet!")
                    
            except Exception as e:
                st.error(f"❌ System Error: {e}")
